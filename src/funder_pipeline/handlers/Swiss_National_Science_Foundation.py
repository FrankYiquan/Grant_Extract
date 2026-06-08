#https://data.snf.ch/grants

import requests
from funder_pipeline.handlers.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from funder_pipeline.utils.helper import escape_xml
import re

def get_Swiss_National_Science_Foundation_grant(projectId, funder_name):
    url = "https://data.snf.ch/api/grants/search" # an api is found on dev tools - subject to change

    normalized_projectId = projectId
    matches = re.findall(r"\d{5,}", projectId)
    if matches:
        normalized_projectId = matches[-1]
   
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
            "filters": {
                "text_search": normalized_projectId
            },
            "includeFacets": True,
            "rows": "10",
            "start": "0"
    }

    response = requests.post(url, headers=headers, json=payload)
    
    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    if response.status_code == 200:
        data = response.json()
        num = data["hits"]["total"]["value"]
        if num > 0:
            # if num > 1:
            #     print(f"Warning: Expected 1 result for projectId {projectId}, but got {num}. Using the first result.")
            grant = data["hits"]["hits"][0]["_source"]
            title = escape_xml(grant.get("title"))
            startDate = grant.get("effective_start_date")
            endDate = grant.get("effective_end_date")
            amount = grant.get("approved_amount")
            status = get_grant_status_from_end_date(endDate)
            if grant.get("application_number"):
                    grant_url = f"https://data.snf.ch/grants/grant/{grant.get('application_number')}"
                    normalized_projectId = grant.get("application_number")
    
    result = f"""<grant>
    <grantId>{normalized_projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.chf</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result

            



# print(get_Swiss_National_Science_Foundation_grant("310030B_182825", "Schweizerischer Nationalfonds zur Förderung der Wissenschaftlichen Forschung"))