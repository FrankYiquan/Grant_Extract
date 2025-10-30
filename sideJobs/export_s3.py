import boto3
import requests
import json
import csv

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

    # Initialize S3 client
    s3 = boto3.client('s3')

    # Start XML content
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<grants xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="schema1.xsd">
'''

    # List objects in the folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    # keep track of length 
    total = len(response['Contents'])
    current = 0
    indent = "    "

    if 'Contents' in response:
        for obj in response['Contents']:
            current += 1
            key = obj['Key']
            # this mean it's a folder
            if key.endswith('/'):
                print (f"Skipping folder placeholder: {key} ({current}/{total})")
                continue  # skip folder placeholders

            print(f"Reading: {key} ({current}/{total})")
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            file_data = file_obj['Body'].read().decode('utf-8')

            # Add file content to XML
            # Split the file_data into lines, add indent to each line, then join
            indented_data = "\n".join(f"{indent}{line}" for line in file_data.splitlines())

            # Append to xml_content
            xml_content += f"{indented_data}\n"
    else:
        print("No files found in this folder.")

    # Close XML
    xml_content += '</grants>'

    # Save to local XML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"XML file created: {output_file}")




def export_grant_asset_linking_from_s3(bucket_name, api_key, output_file=None):
   
    if output_file is None:
            output_file = f'sideJobs/s3/{bucket_name}.csv'
    
    # Initialize S3 client
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=bucket_name)

    # List objects with delimiter to get first-level folders
    response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')

    result = []

    if 'CommonPrefixes' in response:
        for prefix in response['CommonPrefixes']:
            folder_name = prefix['Prefix']

            # List objects inside this folder
            inner_response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

            # Get the first record in the folder (skip the folder itself)
            if 'Contents' in inner_response:
                check_assetId = True
                asset_id = None
                is_exist = False #only check the first record for an folder(asset)
                for obj in inner_response['Contents']:
                    if obj['Key'] != folder_name:  # ignore folder placeholder; the inner_response includes the folder itself, which we don't want
                        file_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                        file_data = file_obj['Body'].read().decode('utf-8') # this is json data
                        data_json = json.loads(file_data)
                        doi = data_json.get("doi")
                        #if the first record in the folder, check for assetId
                        if check_assetId:
                            asset_id = get_assetID(doi, api_key)
                            is_exist = asset_id is not None
                            print(f"DOI: {doi}, Asset ID: {asset_id}")
                            check_assetId = False 
                        
                    result.append({
                        "asset_id": asset_id,
                        "doi": doi,
                        "award_id": data_json.get("award_id", None),
                        "is_exist": is_exist
                    })
                    

        # write to a csv
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["asset_id", "doi", "award_id", "is_exist"])
            writer.writeheader()
            writer.writerows(result)
            print(f"CSV file created: {output_file}")


def get_assetID(doi, api_key):
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
# export_grant_from_s3('brandeis-grants', 'national_institutes_of_health')

# asset id, award id, doi, isexisit

