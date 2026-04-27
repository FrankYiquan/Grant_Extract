import csv
import requests
from datetime import datetime, date
from funderAPI.helper.schema_extract import get_grant_status_from_end_date, get_matched_funder_code
from utils.helper import escape_xml


# # usa spending works for parent organization belong to federal govenrment, in particular the military-related project
# determine what type of grant it is 
def get_us_spending_grant_type(award_id):
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
                "keywords": [award_id],
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
        for award_type, count in count_data.items():
            if count > 0:
               result = award_type_codes.get(award_type)
    return result

def get_US_Spending_grant(award_id, funder_name):

    #normalize award_id: get rid of "-" and spaces
    award_id = award_id.replace("-", "") if "-" in award_id else award_id
    award_id = award_id.replace(" ", "") if " " in award_id else award_id

    award_type_codes = get_us_spending_grant_type(award_id)

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    payload = {
        "filters": {
                "keywords": [award_id],
                "time_period": [
                {
                    "start_date": "2007-10-01",
                    "end_date": "2025-09-30"
                }
                ],
                "award_type_codes": award_type_codes
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
    
    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"
    awardID = award_id

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            grant = data.get("results")[0]
            amount = grant.get("Award Amount")
            title = grant.get("Description")
            title = escape_xml(title)

            awardID = grant.get("Award ID")

            startDate = grant.get("Start Date")
            endDate = grant.get("End Date")
            status = get_grant_status_from_end_date(endDate)
            
            internal_id = grant.get("recipient_id")
            if internal_id:
                grant_url = f"https://www.usaspending.gov/recipient/{internal_id}"
    
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


# print(get_US_Spending_grant("DE-AC52-07NA27344", "U.S. Department of Energy"))
