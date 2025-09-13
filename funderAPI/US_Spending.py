import requests

# # usa spending works for parent organization belong to federal govenrment, in particular the military-related project


def get_us_spending_grant_type(award_id):

    # determine what type of grant it is 

    #this is needed to set the field "award_type_codes" in the payload when search for grant
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

def get_US_Spending_grant(award_id):

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
    title = None

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            grant = data.get("results")[0]
            amount = grant.get("Award Amount")
            title = grant.get("Description")
            startDate = grant.get("Start Date")
    
    return{
        "title": title,
        "amount": amount,
        "start_date": startDate,
        "currency": "USD"
    }


# print(get_US_Spending_grant("80NSSC23K1596"))
