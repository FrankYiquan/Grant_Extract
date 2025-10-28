import boto3

def combine_s3_files_to_xml(bucket_name, folder_name, output_file=None):
   
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


# Example usage:
# combine_s3_files_to_xml('brandeis-grants', 'national_institutes_of_health')

