import requests

def get_Norges_Forskningsrad_grant(projectId):

    normalized_key = projectId.split("-")[-1] if "-" in projectId else projectId

    url = f"https://prosjektbanken.forskningsradet.no/prosjektbanken/rest/projectlist?Kilde=FORISS&distribution=Ar&chart=bar&calcType=funding&Sprak=no&sortBy=score&sortOrder=desc&resultCount=30&offset=0&Fritekst={normalized_key}&source=FORISS&projectId={normalized_key}"

    response = requests.get(url)
    amount = None
    title = None
    startDate = None
    principal_investigator = None

    if response.status_code == 200 and response:
        data = response.json()

        if data['projects']:
            project = data['projects'][0]
            amount = project.get("totalFunding", None)
            title = project.get("title", None)
            startDate = project.get("duration").get('startYear', None)
            principal_investigator = project.get("leadName", None)

    return {
        "title": title,
        "amount": amount,
        "start_date": startDate,
        "principal_investigator": principal_investigator,
        "currency": "NOK"
    }

print(get_Norges_Forskningsrad_grant("RCN-314472"))