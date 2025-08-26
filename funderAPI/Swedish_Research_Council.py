import requests

def extract_Swedish_Research_Council_grant(projectId, apiKey = "Bearer VRSwecrisAPI2025-1"):
    
    normalized_projectId = projectId.split("VR")[1].strip() + "_VR" if projectId.startswith("VR") else projectId
    final_projectId = normalized_projectId + "_VR" if not normalized_projectId.endswith("_VR") else normalized_projectId

    url = f"https://swecris-api.vr.se/v1/projects/{final_projectId}"

    headers = {
    "Authorization": apiKey
    }

    response = requests.get(url, headers=headers)

    startDate = None
    amount = None 
    if response.status_code == 200 and response != None:
        data = response.json()
        startDate = data.get("projectStartDate").split(" ")[0].strip()
        amount = data.get("fundingsSek")
    

    return {
        "startDate": startDate,
        "amount": amount,
        "currency": "kr"
    }


#print(extract_Swedish_Research_Council_grant("2021-03651", "Bearer DTaURVYva7l6qNYX7zdLN8Tg"))

