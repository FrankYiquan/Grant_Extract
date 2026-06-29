from collections import defaultdict
from pathlib import Path
import requests
from funder_pipeline.utils.sqs_config import PRODUCTION_EXLIBRIS_API
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv, logging
from funder_pipeline.utils.logging import log_stage

logger = logging.getLogger(__name__)

def get_assetID(doi, api_key=PRODUCTION_EXLIBRIS_API):
    """
    Given a DOI, fetch the corresponding asset ID using the provided API key.
    """

    base_url = "https://api-na.hosted.exlibrisgroup.com/esploro/v1/assets"
    headers = {
        "Accept": "application/json",
        "Authorization": f"apikey {api_key}"
    }
    params = {"doi": doi}
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        asset_id = None
        
        # Check if there’s at least one record and extract assetId
        if data.get("totalRecordCount", 0) > 0:
            record = data["records"][0]
            asset_id = record.get("originalRepository", {}).get("assetId")
            return asset_id
        else:
            return None

    except requests.exceptions.RequestException as e:
        # print(f"Error fetching asset: {e}")
        return None
    
def run_get_assetID_by_doi(args):
    logger.info("")
    logger.info("=" * 80)

    logger.info(
        "JOB RUN: DOI=%s",
        args.doi,
    )

    success, assetID = is_valid_asset(args.doi)

    log_stage(
        "[1/1] Get Asset ID from Espero",
        {
            "Asset ID": assetID if success else "DOI cannot be found in Espero"
        },
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("JOB COMPLETE")
    logger.info("=" * 80)

def is_valid_asset(doi: str):
    """
    Check if the given doi is valid by making a request to the ExLibris API.
    Parameters:
    - assetID: str, the doi to check
    Returns:
    - bool: True if the doi is valid, False otherwise

    Valid means the doi exits in the system and is an asset associated with a faculty not temproary staff or student.
    """
    asset_id = get_assetID(doi)

    if asset_id:
        return True, asset_id

    return False, None


def filter_invalid_assets(awards, funder_name, start_year, end_year):
    # Group awards by doi
    awards_sort_by_doi = defaultdict(list)
    for award in awards:
        awards_sort_by_doi[award["doi"].split("https://doi.org/")[-1]].append(award)
    
    # filtering
    valid_awards = []
    invalid_dois = set()

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_doi = {
            executor.submit(is_valid_asset, doi): doi 
            for doi in awards_sort_by_doi.keys()
        }

        for future in as_completed(future_to_doi):
            doi = future_to_doi[future]
            try:
                is_valid, asset_id = future.result()
                if is_valid:
                    for award in awards_sort_by_doi[doi]:
                      award["asset_id"] = asset_id
                    valid_awards.extend(awards_sort_by_doi[doi])
                else:
                    invalid_dois.add(doi)
            except Exception as e:
                # print(f"Error processing DOI {doi}: {e}")
                invalid_dois.add(doi)
    
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
