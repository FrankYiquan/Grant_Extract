import requests
from funder_pipeline.handlers.helper.schema_extract import get_grant_status_from_end_date, get_matched_funder_code
from funder_pipeline.utils.helper import escape_xml
    

# # usa spending works for parent organization belong to federal govenrment, in particular the military-related project
# determine what type of grant it is 
def get_us_spending_grant_type(award_ids: list[str]) -> list[list[str]]:
    #this is needed to set the field "award_type_codes" in the payload when search for grant
    # info referenced from https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award.md
    award_type_codes = {
        "contracts": ["A", "B", "C", "D"],
        "loans": ["07", "08"],
        "idvs": ["IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D", "IDV_E"],
        "grants": ["02", "03", "04", "05"],
        "other": ["06", "10"],
        "direct_payments": ["09", "11", "-1"]
    }

    count_url = "https://api.usaspending.gov/api/v2/search/spending_by_award_count/"
    count_payload = {
            "filters": {
                "keywords": award_ids,
                "time_period": [
                {
                    "start_date": "2007-10-01",
                    "end_date": "2025-09-30"
                }
                ]
            },
            "spending_level": "awards",
            "auditTrail": "Results View - Tab Counts"
    }
    count_response = requests.post(count_url, json=count_payload)
    result = []
    if count_response.status_code == 200:
        count_data = count_response.json().get("results", {})
        
        valid_award_types = set(award_type for award_type, count in count_data.items() if count > 0)

        if len(valid_award_types) > 5:
            return [] # this indicate the award_id is not specific enough, e.g. 00001
        
        result.extend(award_type_codes[award_type] for award_type in valid_award_types if award_type_codes.get(award_type, []))

    return result

def normalize_id(award_id: str, funder_name: str) -> list[str]:
    distracted_start_word = ["Contract No.", "No.", "ECA", ".", "AFOSR"]

    for word in distracted_start_word:
        if award_id.startswith(word):
            award_id = award_id[len(word):].strip()
            break

    award_id = award_id.strip() 
    result = [award_id]
    if funder_name == "U.S. Department of Energy" and not award_id.startswith("DE"):
        # DE is the prefix for Department of Energy in USAspending, but sometimes it is replaced by DOE
        if award_id.startswith("DOE"):
            award_id = award_id.replace("DOE", "DE")
            result.append(award_id)
        # AC02 is the most common prefix
        result.append("DEAC02" + award_id)
        result.append("DE" + award_id)
    
    return result

def extract_US_Spending_award(award_id: str, funder_name: str) -> str:
    # clean out the characters that are not acceptable by API
    distracted_characters = ["-", " "]
    cleaned_award_id = award_id
    for ch in distracted_characters:
        if ch in award_id:
            cleaned_award_id = award_id.replace(ch, "")

    normalize_award_ids = normalize_id(cleaned_award_id, funder_name)
    print(f"Normalized award ID: {normalize_award_ids}")

    award_type_codes = get_us_spending_grant_type(normalize_award_ids)
    print(award_type_codes)

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"
    awardID = award_id

    # sometimes, DE appear in other non-DE award ID; treat it as DE award ID
    if cleaned_award_id.startswith("DE") and funder_name != "U.S. Department of Energy":
        funderCode = get_matched_funder_code("U.S. Department of Energy")

    for award_type_code in award_type_codes:
        payload = {
            "filters": {
                    "keywords": normalize_award_ids,
                    "time_period": [
                    {
                        "start_date": "2007-10-01",
                        "end_date": "2025-09-30"
                    }
                    ],
                    "award_type_codes": award_type_code
                },
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Award Amount",
                    "Total Outlays",
                    "Description",
                    "Award Type",
                    "Contract Award Type",
                    "Recipient UEI",
                    "Recipient Location",
                    "Primary Place of Performance",
                    "def_codes",
                    "COVID-19 Obligations",
                    "COVID-19 Outlays",
                    "Infrastructure Obligations",
                    "Infrastructure Outlays",
                    "Awarding Agency",
                    "Awarding Sub Agency",
                    "Start Date",
                    "End Date",
                    "NAICS",
                    "PSC",
                    "Assistance Listings",
                    "recipient_id",
                    "prime_award_recipient_id"
                ],
                "page": 1,
                "limit": 100,
                "sort": "Award Amount",
                "order": "desc",
                "spending_level": "awards",
                "auditTrail": "Results Table - Spending by award search"
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("results"):

                # if too many results are returned, it is likely that the award_id is not specific enough, e.g. DEFG02 -> asummed it's not found.
                if len(data["results"]) > 10:
                    print(f"Too many results returned for award ID {award_id}, likely due to non-specific award ID. Skipping.")
                    break

                grant = next(
                    (grant for grant in data["results"] if cleaned_award_id in grant.get("Award ID")), 
                    None
                )
                
                if grant:
                    amount = grant.get("Award Amount")
                    title = grant.get("Description")
                    title = escape_xml(title)

                    awardID = grant.get("Award ID")

                    startDate = grant.get("Start Date")
                    endDate = grant.get("End Date")
                    status = get_grant_status_from_end_date(endDate)
                    
                    internal_id = grant.get("generated_internal_id")
                    if internal_id:
                        grant_url = f"https://www.usaspending.gov/award/{internal_id}/"
                    
                    break  # stop after finding the first match for the current award type code

    result = f"""<grant>
    <grantId>{awardID}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.usd</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result


# print(extract_US_Spending_award("DE-AC02-06CH11357", "Army Research Office"))
# print(normalize_id("05CH11231", "U.S. Department of Energy"))
