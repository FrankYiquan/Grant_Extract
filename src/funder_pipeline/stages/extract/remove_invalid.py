from collections import defaultdict
from pathlib import Path
import requests
from funder_pipeline.utils.sqs_config import PRODUCTION_EXLIBRIS_API
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

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
            # print(f"Error checking asset ID {doi}: Received status code {response.status_code}")
            return False
        
        return response.status_code == 200 and response.json().get("totalRecordCount", 0) > 0
    except Exception as e:
        # print(f"Error checking asset ID {doi}: {e}")
        return False


def filter_invalid_assets(awards, funder_name, start_year, end_year):
    # Group awards by doi
    awards_sort_by_doi = defaultdict(list)
    for award in awards:
        awards_sort_by_doi[award["doi"]].append(award)
    
    # filtering
    valid_awards = []
    invalid_dois = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_doi = {
            executor.submit(is_valid_asset, doi): doi 
            for doi in awards_sort_by_doi.keys()
        }

        for future in as_completed(future_to_doi):
            doi = future_to_doi[future]
            try:
                if future.result():
                    valid_awards.extend(awards_sort_by_doi[doi])
                else:
                    invalid_dois.append(doi)
            except Exception as e:
                # print(f"Error processing DOI {doi}: {e}")
                invalid_dois.append(doi)
    
    # write invalid assets doi to csv
    invalid_asset_output_dir = (
        Path("outputs")
        / "invalid_assets"
        / f"{funder_name}_{start_year}_{end_year}_invalid_assets.csv"
    )
    with open(invalid_asset_output_dir, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["doi"])
        for doi in invalid_dois:
            writer.writerow([doi])
    
    return valid_awards, invalid_dois, invalid_asset_output_dir



    
    
    
    






# print(is_valid_asset("10.1093/mnras/stz272"))