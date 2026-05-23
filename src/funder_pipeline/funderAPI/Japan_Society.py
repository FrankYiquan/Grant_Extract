from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from funder_pipeline.utils.helper import escape_xml


# API response has two language option: english and japanese
# prioritize english or fall back to japanese if english not available
def get_summary(grant):
    for lang in ['en', 'ja']:
        for s in grant.findall('summary'):
            if s.get('{http://www.w3.org/XML/1998/namespace}lang') == lang:
                return s
    return grant.find('summary')

def get_jsps_grant(projectId, funder_name, apiKey="pH9N5nJjVvOCjTpZ91Fp"):
    normalized_key = projectId.split("JP")[1] if "JP" in projectId else projectId

    url = f"https://kaken.nii.ac.jp/opensearch/?appid={apiKey}&kw={normalized_key}&format=xml"

    response = requests.get(url)

    amount = None
    startDate = None
    endDate = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"
    award_id = projectId

    if response.status_code == 200:
        root = ET.fromstring(response.text)

        grant = root.find('grantAward')

        if grant is not None and int(root.findtext('totalResults', default = 0)) == 1:
            grant_summary = get_summary(grant)

            award_id = grant.findtext('identifier/normalizedValue') or projectId
            if award_id in projectId or projectId in award_id:
                grant_url = grant.findtext('urlList/url')

                if grant_summary is not None:
                    title = grant_summary.findtext('title')
                    title = escape_xml(title)

                    amount = grant_summary.findtext('overallAwardAmount/totalCost')
                
                    # sometimes, startDate and endDate only occur at the japanese summary
                    startDate = grant.findtext('.//periodOfAward/startDate')
                    endDate   = grant.findtext('.//periodOfAward/endDate')

                    if not startDate:
                        startDate = grant.findtext('.//startFiscalYear')
                        startDate = f"{startDate}-01-01" if startDate else None
                    
                    if not endDate:
                        endDate = grant.findtext('.//endFiscalYear')
                        endDate = f"{endDate}-12-31" if endDate else None

                    status = get_grant_status_from_end_date(endDate)

    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.jpy</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result


print(get_jsps_grant("25120007", "Japan Society for the Promotion of Science"))
