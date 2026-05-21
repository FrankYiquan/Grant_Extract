import requests
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)

def get_ARC_grant(projectId, funder_name):

    url = f"https://dataportal.arc.gov.au/NCGP/API/grants/{projectId}"

    response = requests.get(url)
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
        grant = data.get("data").get("attributes",{})
       
        amount = grant.get("funding-current")
        startDate = grant.get("project-start-date")
        endDate = grant.get("anticipated-end-date")
        title = escape_xml(grant.get("project-title"))
        status = get_grant_status_from_end_date(endDate)
        grant_url = "https://dataportal.arc.gov.au/RGS/Web/Grants/" + data.get("data").get("id")
    

    result = f"""<grant>
    <grantId>{projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.aud</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result


print(get_ARC_grant("DP150103442", "Australian Research Council")) 