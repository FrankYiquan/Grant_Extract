import requests
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from datetime import datetime

def extract_Norges_Forskningsrad_award(projectId, funder_name):
    normalized_key = projectId.split("-")[-1] if "-" in projectId else projectId

    url = f"https://prosjektbanken.forskningsradet.no/prosjektbanken/rest/projectlist?Kilde=FORISS&distribution=Ar&chart=bar&calcType=funding&Sprak=no&sortBy=score&sortOrder=desc&resultCount=30&offset=0&Fritekst={normalized_key}&source=FORISS&projectId={normalized_key}"

    response = requests.get(url)

    amount = None
    principal_investigator = None
    startDate = None
    endDate = None
    title = None
    status = "ACTIVE"
    grant_url = None
    funderCode =  get_matched_funder_code(funder_name)

    if response.status_code == 200:
        data = response.json()

        if data['projects']:
            project = data['projects'][0]
            if str(project.get("id")) in projectId:
                amount = project.get("totalFunding")
                title = escape_xml(project.get("title"))
                startDate_str = project.get("duration").get('startYear')
                startDate = f"{startDate_str}-01-01"
                endDate_str = project.get("duration").get('endYear')
                if endDate_str:
                    endDate = f"{endDate_str}-01-01"
                    status = get_grant_status_from_end_date(endDate)
                # principal_investigator = project.get("leadName")
                grant_url = "https://prosjektbanken.forskningsradet.no/en/project/FORISS/" + str(project.get("id"))

    result = f"""<grant>
    <grantId>{projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.nok</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result

# print(extract_Norges_Forskningsrad_award("RCN-314472", "Norges Forskningsråd"))