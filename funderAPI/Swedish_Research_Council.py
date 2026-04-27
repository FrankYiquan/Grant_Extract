from datetime import date
import requests
import re
from utils.helper import escape_xml
from funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)


def normalize_id(award_id: str) -> str:
    m =  re.search(r'\d{4}-\d{5}', award_id)
    if m:
        return m.group(0) + "_VR"
    return award_id

def get_Swedish_Research_Council_grant(projectId, funder_name, apiKey = "Bearer DTaURVYva7l6qNYX7zdLN8Tg"):
    awardID = normalize_id(projectId)

    url = f"https://swecris-api.vr.se/v1/projects/{awardID}"

    headers = {
    "Authorization": apiKey
    }

    response = requests.get(url, headers=headers)
    print(url)

    amount = None
    principal_investigator = None
    startDate = None
    endDate = None
    title = None
    status = "ACTIVE"
    grant_url = None
    funderCode = get_matched_funder_code(funder_name)

    if response.status_code == 200:
        data = response.json()

        title = data.get("projectTitleEn")
        if not title:
            title = data.get("projectTitleSv")
        title = escape_xml(title)

        startDate = data.get("projectStartDate").split(" ")[0].strip()
        endDate = data.get("projectEndDate").split(" ")[0].strip()
        status = get_grant_status_from_end_date(endDate)

        amount = data.get("fundingsSek")
        
        awardID = data.get('projectId')
        if awardID:
            grant_url = f"https://www.vr.se/english/swecris.html#/project/{awardID}"
    

    result = f"""<grant>
    <grantId>{awardID if amount else projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.kr</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result


print(get_Swedish_Research_Council_grant("VR 2022-03845", "Vetenskapsrådet"))

