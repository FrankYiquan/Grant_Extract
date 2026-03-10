import requests
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.sqs_config import PRODUCTION_EXLIBRIS_API

# def import_all_asset_grant_linking(linking_file, api_key):

#     with open(linking_file, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)

#         #for row in reader:
#             # call the lining methiod 


def import_asset_grant_linking(assetId, awardId_list, api_key=PRODUCTION_EXLIBRIS_API):

    """
    Links a list of award IDs to a given asset ID using the Ex Libris Esploro API.
    """

    url = f"https://api-na.hosted.exlibrisgroup.com/esploro/v1/assets/{assetId}?op=patch&action=add"

    headers = {
        "Accept": "application/json",
        "Authorization": f"apikey {api_key}"
    }

    # transfrorm awardId_list to the expected json format
    grants = [{"awardnumber": awardId} for awardId in awardId_list]

    payload = {
        "records": [
            {
                "fundingreferenceList": grants
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 

        if response.status_code == 200:
            print(f"Successfully linked awards {awardId_list} to asset {assetId}.")
        else:
            print(f"Failed to link awards {awardId_list} to asset {assetId}. Status code: {response.status_code}")  
    except requests.exceptions.RequestException as e:
        print(f"Error linking awards {awardId_list} to asset {assetId}: {e}")


def process_asset_grant_file(api_key=PRODUCTION_EXLIBRIS_API, max_workers=10):

    CSV_PATH = "sideJobs/s3/asset-grant-linking.csv"

    asset_awards = defaultdict(list)

    # Read CSV + group awards by asset_id
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            asset_id = row["asset_id"]
            award_id = row["award_id"]

            if asset_id and award_id:
                asset_awards[asset_id].append(award_id)

    print(f"Found {len(asset_awards)} assets to update")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = []

        for asset_id, award_list in asset_awards.items():
            futures.append(
                executor.submit(
                    import_asset_grant_linking,
                    asset_id,
                    award_list,
                    api_key
                )
            )

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("Error in worker:", e)


# process_asset_grant_file()