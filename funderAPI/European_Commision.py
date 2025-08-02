
import re
import requests
import xml.etree.ElementTree as ET



def extract_erc_id(text):
    match = re.search(r'(?:\bERC[\s\u2013\u2014-]*)?(\d+)\b', text, re.IGNORECASE)
    return match.group(1) if match else None

# print(extract_erc_id("ERC 101089007"))

def get_eu_commision_grant(projectId):
    ns = {'ns': 'http://cordis.europa.eu'}

    grant_id = extract_erc_id(projectId)

    url = f"https://cordis.europa.eu/project/id/{grant_id}?format=xml"

    response = requests.get(url)
    amount = None
    startDate = None
   
    if response.status_code == 200 and response != None:
        root = ET.fromstring(response.text)
       
        amount_elem = root.find('ns:totalCost', ns)
        startDate_elem = root.find('ns:startDate', ns)

        amount = amount_elem.text if amount_elem is not None else None
        startDate = startDate_elem.text if startDate_elem is not None else None
    return {
        "amount": amount,
        "startDate": startDate,
        "currency": "Euro"
    }

# print(get_eu_commision_grant("EERC\u2013948254"))





