#https://data.snf.ch/grants

import requests

def get_Swiss_National_Science_Foundation_grant(projectId):
    url = "https://data.snf.ch/solr/search/select"

    normalized_projectId = projectId
    if "_"  in projectId:
        normalized_projectId = projectId.split("_")[1]
   

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    payload = {
        "q": f"Category:search AND Entity:Grant AND GrantNumber:{normalized_projectId}",
        "start": "0",
        "sort": "StateSortNumber asc,EffectiveGrantStartDate desc",
        "rows": "10"
    }

    response = requests.post(url, headers=headers, data=payload)\
    
    if response.status_code == 200:
        data = response.json()
        if data["response"]["numFound"] > 0:
            grant = data["response"]["docs"][0]
            title = grant.get("Title")
            startDate = grant.get("EffectiveGrantStartDate").split("T")[0]
            amount = grant.get("AmountGrantedAllSets")
            principal_investigator = grant.get("AllApplicantName_mvf")

            return {
                "title": title,
                "startDate": startDate,
                "amount": amount,
                "currency": "CHF", #Swiss Franc
                "principal_investigator": principal_investigator
            }
    return {
        "title": None,
        "startDate": None,
        "amount": None,
        "currency": "CHF", #Swiss Franc
        "principal_investigator": None
    }


#print(get_Swiss_National_Science_Foundation_grant("205321_192371"))