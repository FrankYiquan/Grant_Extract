
import requests
def get_NOVWO_grant(projectId):

    normalized_key = projectId.split("-")[-1] if "-" in projectId else projectId
    url = f"https://nwopen-api.nwo.nl/NWOpen-API/api/Projects?project_id={normalized_key}"

    response = requests.get(url)
    amount = None
    startDate = None
    title = None
    principal_investigator = None

    if response.status_code == 200 and response:
        data = response.json()
        if data["meta"]["count"] > 0:
            project = data['projects'][0]

            amount = project.get("award_amount", None)
            title = project.get("title", None)
            startDate = project.get("start_date", None).split("T")[0] 
            principal_investigator = next(
                (person.get("first_name", "") + " " + person.get("last_name", "")
                for person in project.get("project_members", [])
                if person.get("role", "").lower() == "project leader"),
                None
            )
    
    return {
        "title": title,
        "amount": amount,
        "start_date": startDate,
        "principal_investigator": principal_investigator,
        "currency": "EUR"
    }

# print(get_NOVWO_grant("Veni 2020-VI.Veni.202.179"))




