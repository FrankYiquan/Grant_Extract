import requests
from utils.sqs_config import PRODUCTION_EXLIBRIS_API

def is_valid_asset(doi: str) -> bool:
    """
    Check if the given doi is valid by making a request to the ExLibris API.
    Parameters:
    - assetID: str, the doi to check
    Returns:
    - bool: True if the doi is valid, False otherwise

    Valid means the doi exits in the system and is an asset associated with a faculty not temproary staff or student.
    """
    url = f"https://api-na.hosted.exlibrisgroup.com/esploro/v1/assets?doi={doi}"
    headers = {
        "Authorization": f"apikey {PRODUCTION_EXLIBRIS_API}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error checking asset ID {doi}: Received status code {response.status_code}")
            return False
        
        return response.status_code == 200 and response.json().get("totalRecordCount", 0) > 0
    except Exception as e:
        print(f"Error checking asset ID {doi}: {e}")
        return False


# print(is_valid_asset("10.1093/mnras/stz272"))