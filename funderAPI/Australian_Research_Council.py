import requests

def get_ARC_grant(projectId):

    url = f"https://dataportal.arc.gov.au/NCGP/API/grants/{projectId}"

    response = requests.get(url)
    amount = None
    startDate = None
    

    if response.status_code == 200:
        data = response.json()
        grant = data.get("data").get("attributes",{})
       
        amount = grant.get("funding-current")
        startDate = grant.get("project-start-date")
    

    return{
        "amount": amount,
        "startDate": startDate,
        "currency": "AUD"
    }


print(get_ARC_grant("CE170100013")) 