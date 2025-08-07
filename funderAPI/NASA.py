import requests

def extract_NASA_grant(projectId):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    payload ={
        "filters": {
            "keywords": [projectId],
            "award_type_codes": ["02", "03", "04", "05"]
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Start Date", "End Date"],
        "limit": 1
    }

    response = requests.post(url, json=payload)

    amount = None
    startDate = None
    if response.status_code == 200 and response:
        data = response.json()

        grant = data.get("results")[0]
        amount = grant.get("Award Amount")
        startDate = grant.get("Start Date")

    return {
        "startDate": startDate,
        "amount": amount,
        "currency": "USD"
    }



print(extract_NASA_grant("80NSSC23K1596"))