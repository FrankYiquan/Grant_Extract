from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
import requests
import json
import csv

from funder_pipeline.utils.sqs_config import PRODUCTION_EXLIBRIS_API

def export_grant_from_s3(bucket_name, folder_name, output_file=None):
    """
    Retrieve all files from an S3 folder and combine them into a single XML file.

    Parameters:
    - bucket_name: str, name of the S3 bucket
    - folder_name: str, folder path in the bucket (e.g., 'national_institute_of_health')
    - output_file: str, local filename to save the combined XML
    """

    if output_file is None:
        output_file = f'sideJobs/s3/{folder_name}.xml'

    # Ensure folder_name ends with '/'
    if not folder_name.endswith('/'):
        folder_name += '/'

    s3 = boto3.client('s3')

    # Use paginator (handles >1000 objects automatically)
    paginator = s3.get_paginator('list_objects_v2')

    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<grants xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="schema1.xsd">
'''
    xml_footer = '</grants>'

    indent = "    "
    total = 0

    # Open file early → avoids storing everything in memory
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_header)

        for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_name):
            for obj in page.get('Contents', []):
                key = obj['Key']

                # Skip folder placeholders
                if key.endswith('/'):
                    continue

                total += 1
                print(f"Reading: {key} (#{total})")

                file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                file_data = file_obj['Body'].read().decode('utf-8')

                # Indent each line
                indented_data = "\n".join(
                    f"{indent}{line}" for line in file_data.splitlines()
                )

                f.write(f"{indented_data}\n")

        f.write(xml_footer)

    print(f"XML file created: {output_file}")
    print(f"Total files processed: {total}")


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
        print(f"Error fetching asset: {e}")
        return None
    
def process_folder(s3, bucket_name, folder_name, api_key = PRODUCTION_EXLIBRIS_API):
    """Process one folder (asset)"""
    inner_response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    results = []
    asset_id = None
    is_exist = False
    check_assetId = True

    if 'Contents' in inner_response:
        for obj in inner_response['Contents']:
            if obj['Key'] == folder_name:
                continue

            file_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            file_data = file_obj['Body'].read().decode('utf-8')
            data_json = json.loads(file_data)

            doi = data_json.get("doi")

            # only call API ONCE per folder
            if check_assetId:
                asset_id = get_assetID(doi, api_key)
                is_exist = asset_id is not None
                check_assetId = False

            results.append({
                "asset_id": asset_id,
                "doi": doi,
                "award_id": data_json.get("awardnumber"),
                "is_exist": is_exist
            })

    return results


def export_grant_asset_linking_from_s3(bucket_name, api_key = PRODUCTION_EXLIBRIS_API, output_file=None, max_workers=10):

    if output_file is None:
        output_file = f'sideJobs/s3/{bucket_name}.csv'

    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')

    all_results = []

    if 'CommonPrefixes' in response:

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for prefix in response['CommonPrefixes']:
                folder_name = prefix['Prefix']
                futures.append(
                    executor.submit(process_folder, s3, bucket_name, folder_name, api_key)
                )

            for future in as_completed(futures):
                all_results.extend(future.result())

    # write CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["asset_id", "doi", "award_id", "is_exist"])
        writer.writeheader()
        writer.writerows(all_results)

    print(f"CSV file created: {output_file}")

    
                   
# Example usage:
# export_grant_from_s3('brandeis-grants', 'national_institutes_of_health')

# asset id, award id, doi, isexisit
export_grant_asset_linking_from_s3('asset-grant-linking')
