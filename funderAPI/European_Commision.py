import re
import requests
import xml.etree.ElementTree as ET
from funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)

def extract_erc_id(text):
    m = re.search(r'(\d{6,})', text)
    return m.group(1) if m else None

# print(extract_erc_id("ERC 101089007"))

def get_eu_commision_grant(award_id: str, funder_name: str):
    ns = {'ns': 'http://cordis.europa.eu'}

    normalized_award_id = extract_erc_id(award_id)

    url = f"https://cordis.europa.eu/project/id/{normalized_award_id}?format=xml"

    response = requests.get(url)
    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = None
    status = "ACTIVE"
   
    if response.status_code == 200 and response != None:
        root = ET.fromstring(response.text)
       
        amount_elem = root.find('ns:totalCost', ns)
        startDate_elem = root.find('ns:startDate', ns)
        endDate_elem = root.find('ns:endDate', ns)
        grant_url = f"https://cordis.europa.eu/project/id/{normalized_award_id}"
        title_elem = root.find('ns:title', ns)
        funderCode = get_matched_funder_code(funder_name)
        
        amount = amount_elem.text if amount_elem is not None else None
        startDate = startDate_elem.text if startDate_elem is not None else None
        endDate = endDate_elem.text if endDate_elem is not None else None
        title = title_elem.text if title_elem is not None else None

        status = get_grant_status_from_end_date(endDate)

    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result

# print(get_eu_commision_grant("306478", "European Research Council"))





