import requests
from funder_pipeline.utils.helper import escape_xml
from datetime import datetime
from dateutil.relativedelta import relativedelta
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)

def get_Bill_and_Melinda_Gates_Foundation_grant(projectId, funder_name):

    projectId = projectId.split(",")[0].strip() if "," in projectId else projectId
    projectId = projectId.replace(" ", "") if " " in projectId else projectId

    

    url = f"https://www.gatesfoundation.org/api/grantssearch?date&displayedTaxonomy&listingId=d2a41504-f557-4f1e-88d6-ea109d344feb&loadAllPages=false&page=1&pageId=31242fca-dcf8-466a-a296-d6411f85b0a5&perPage=10&q={projectId}&sc_site=gfo&showContentTypes=false&showDates=false&showImages&showSummaries=false&sortBy=date-desc&sortOrder=desc"

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
        if data["totalResults"] > 0:
            grant = data['results'][0]
            title = escape_xml(grant.get("grantTopic"))
            amount = grant.get("awardedAmount").split("$")[-1] if "$" in grant.get("awardedAmount", "") else grant.get("awardedAmount")
            startDate_str = grant.get("date")
            startDate = datetime.strptime(startDate_str, "%B %Y").strftime("%Y-%m-01")
            if grant.get("grantStatus") == "Closed":
                duration = int(grant.get("grantDuration"))
                endDate_str = startDate_str + relativedelta(months=duration)
                endDate = endDate_str.strftime("%Y-%m-%d")
                status = "HISTORY"
            grant_url = "https://www.gatesfoundation.org" + grant.get("url")




    
    result = f"""<grant>
    <grantId>{projectId}</grantId>
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

            
print(get_Bill_and_Melinda_Gates_Foundation_grant("INV-046299", "Bill and Melinda Gates Foundation"))