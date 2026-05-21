
import requests
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)

def get_NOVWO_grant(projectId, funder_name):

    normalized_key = projectId.split("-")[-1] if "-" in projectId else projectId
    url = f"https://nwopen-api.nwo.nl/NWOpen-API/api/Projects?project_id={normalized_key}"

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["meta"]["count"] > 0:
            project = data['projects'][0]

            amount = project.get("award_amount")
            title = escape_xml(project.get("title"))
            startDate = project.get("start_date").split("T")[0] 
            endDate = project.get("end_date")
            if endDate:
                endDate = endDate.split("T")[0]
            status = get_grant_status_from_end_date(endDate)
            projectId = project.get("project_id")
            projectId_param = projectId.replace(".", "") if "." in projectId else projectId
            grant_url = "https://www.nwo.nl/en/projects/" + projectId_param.lower()
            # principal_investigator = next(
            #     (person.get("first_name", "") + " " + person.get("last_name", "")
            #     for person in project.get("project_members", [])
            #     if person.get("role", "").lower() == "project leader"),
            #     None
            # )
    
    result = f"""<grant>
    <grantId>{projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.eur</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result

# print(get_NOVWO_grant("1292.19.202", "Nederlandse Organisatie voor Wetenschappelijk Onderzoek"))




