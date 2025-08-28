
import requests
import xml.etree.ElementTree as ET


def get_jsps_grant(projectId, apiKey = "pH9N5nJjVvOCjTpZ91Fp"):

    normalized_key = projectId.split("JP")[1] if "JP" in projectId else projectId

    url = f"https://kaken.nii.ac.jp/opensearch/?appid={apiKey}&kw={normalized_key}&format=xml"
    # print(url)

    response = requests.get(url)
    amount = None
    startDate = None


    if response.status_code == 200 and response != None:
        root = ET.fromstring(response.text)
        grant = root.find('grantAward').find('summary')
        
        total_amount = grant.find('overallAwardAmount/totalCost')
        start_date = grant.find('periodOfAward/startDate')
        if start_date == None:
            start_date = grant.find('periodOfAward/startFiscalYear')

        amount = total_amount.text if total_amount is not None else None
        startDate = start_date.text if start_date is not None else None

       
            
    return {
        "amount": amount,
        "startDate": startDate,
        "currency": "JPY"
    }

# print(get_jsps_grant("JP21H05085"))
