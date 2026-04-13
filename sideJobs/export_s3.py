import boto3
import requests
import json
import csv

from utils.sqs_config import PRODUCTION_EXLIBRIS_API

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
    

    
                   
# Example usage:
export_grant_from_s3('brandeis-grants', 'national_institutes_of_health')

# asset id, award id, doi, isexisit
# export_grant_asset_linking_from_s3('asset-grant-linking')
