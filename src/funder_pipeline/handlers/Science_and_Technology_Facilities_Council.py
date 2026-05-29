import requests
from funder_pipeline.handlers.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from funder_pipeline.utils.helper import escape_xml
from datetime import datetime


def extract_Science_and_Technology_Facilities_Council_award(grantId, funder_name):
    url = f"https://gtr.ukri.org/api/projects?ref={grantId}"

    response = requests.get(url, headers={"Accept": "application/json"})

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
        project = data["projectOverview"]["projectComposition"]["project"]

        title = escape_xml(project["title"])
        amount = project["fund"]["valuePounds"]

        startDate = datetime.utcfromtimestamp(
            project["fund"]["start"] / 1000
        ).strftime("%Y-%m-%d")

        end = project.get("fund", {}).get("end")
        if end:
            endDate = datetime.utcfromtimestamp(
                end / 1000
            ).strftime("%Y-%m-%d")

        if endDate:
            status = get_grant_status_from_end_date(endDate)

        grant_url = project.get("resourceUrl").replace("/api", "")
        grantId = project.get("grantReference")


        # people = data["projectOverview"]["projectComposition"]["personRoles"]

        # for person in people:
        #    if any(
        #             role["name"].lower() in ["principal_investigator", "principal investigator"]
        #             for role in person["roles"]
        #         ):
        #        name = person["fullName"]
        #        orcidId = person["orcidId"]

    result = f"""<grant>
    <grantId>{grantId}</grantId>
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

       

funder_name = "Science and Technology Facilities Council"
grant_id = "GRIDPP"
print(extract_Science_and_Technology_Facilities_Council_award(grant_id, funder_name))  
