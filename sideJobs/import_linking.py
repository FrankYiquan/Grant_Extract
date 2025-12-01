import requests
import csv

# def import_all_asset_grant_linking(linking_file, api_key):

#     with open(linking_file, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)

#         #for row in reader:
#             # call the lining methiod 


def import_asset_grant_linking(assetId, awardId_list, api_key):

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

    



api_key = ""
assetId = "9924085974501921"
awardId_list = ['DA041022', 'DA041025', 'DA041028', 'DA041048', 'DA041089', 'DA041093', 'DA041106', 'DA041117', 'DA041120', 'DA041123', 'DA041134', 'DA041147', 'DA041148', 'DA041156', 'DA041174', 'NS112810']


import_asset_grant_linking(assetId, awardId_list, api_key)