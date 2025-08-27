import requests
import datetime

def get_Science_and_Technology_Facilities_Council_grant(grantId):
    url = f"https://gtr.ukri.org/api/projects?ref={grantId}"

    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code == 200:
        data = response.json()
        project = data["projectOverview"]["projectComposition"]["project"]

        title = project["title"]
        amount = project["fund"]["valuePounds"]

        start = datetime.datetime.utcfromtimestamp(project["fund"]["start"]/1000)
        #end = datetime.datetime.utcfromtimestamp(project["fund"]["end"]/1000)

        people = data["projectOverview"]["projectComposition"]["personRoles"]

        for person in people:
           if any(
                    role["name"].lower() in ["principal_investigator", "principal investigator"]
                    for role in person["roles"]
                ):
               name = person["fullName"]
               orcidId = person["orcidId"]

        return {
            "title": title,
            "startDate": start.strftime("%Y-%m-%d"),
            #"endDate": end.strftime("%Y-%m-%d"),
            "amount": amount,
            "currency": "GBP", #pounds
            "principal_investigator": name,
            "orcid": orcidId
        }

# print(get_Science_and_Technology_Facilities_Council_grant("ST/Y001508/1"))  
