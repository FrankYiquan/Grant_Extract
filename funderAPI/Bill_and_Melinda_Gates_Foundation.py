import requests

def get_Bill_and_Melinda_Gates_Foundation_grant(projectId):

    projectId = projectId.split(",")[0].strip() if "," in projectId else projectId
    projectId = projectId.replace(" ", "") if " " in projectId else projectId

    

    url = f"https://www.gatesfoundation.org/api/grantssearch?date&displayedTaxonomy&listingId=d2a41504-f557-4f1e-88d6-ea109d344feb&loadAllPages=false&page=1&pageId=31242fca-dcf8-466a-a296-d6411f85b0a5&perPage=10&q={projectId}&sc_site=gfo&showContentTypes=false&showDates=false&showImages&showSummaries=false&sortBy=date-desc&sortOrder=desc"

    response = requests.get(url)

    amount = None
    startDate = None
    title = None
  

    if response.status_code == 200 and response:
        data = response.json()
        if data["totalResults"] > 0:
            grant = data['results'][0]
            title = grant.get("grantTopic")
            amount = grant.get("awardedAmount").split("$")[-1] if "$" in grant.get("awardedAmount", "") else grant.get("awardedAmount")
            startDate = grant.get("date")
    
    return {
        "title": title,
        "amount": amount,
        "start_date": startDate,
        "currency": "USD"
    }

            
print(get_Bill_and_Melinda_Gates_Foundation_grant("INV-046299"))