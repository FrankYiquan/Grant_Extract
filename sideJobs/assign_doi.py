import requests
import pandas as pd

from sideJobs.export_s3 import get_assetID
import csv

def assign_doi_to_asset(title):
    """
    Given a title, use openalex API to find the corresponding DOI.
    """

    url = f" https://api.openalex.org/works?filter=title.search:{title}"

    response = requests.get(url)
    doi = None
    if response.status_code == 200:
        data = response.json()
        count = data.get("meta", {}).get("count", 0)
        if count == 0:
            return None
        doi = data.get("results")[0].get("doi", None)
        if doi:
            doi = doi.split("https://doi.org/")[-1]
        return doi
    return doi
        
def populate_doi_column(csv_input_path="resources/assets_without_doi.csv", csv_output_path="sideJobs/s3/asset_doi.csv"):
    """
    Reads a CSV file, fetches DOI for each title, and writes back to a new CSV.
    """
    # Load the CSV
    
    df = pd.read_csv(csv_input_path)

    # Ensure 'doi' column exists
    if 'DOI' not in df.columns:
        df['DOI'] = None

    # Apply the DOI assignment function to each row
    df['DOI'] = df['Title'].apply(assign_doi_to_asset)

    # Save the updated CSV
    df.to_csv(csv_output_path, index=False)
    print(f"CSV updated and saved to {csv_output_path}")

def get_brandeis_asset_doi(institutionsId="I6902469", startyear=2017, endYear=2025):
    base_url = "https://api.openalex.org/works"
    filter_str = f"institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"
    select_fields = "id,doi,title,publication_year,grants"

    output = []
    cursor = "*"  # initial cursor

    while cursor:
        url = f"{base_url}?filter={filter_str}&select={select_fields}&per-page=200&cursor={cursor}"
        response = requests.get(url)
        data = response.json()

        for asset in data.get('results', []):
            output.append({
                "openAlex_id": asset.get('id'),
                'doi': asset.get('doi'),
                'title': asset.get('title'),
                'publication_year': asset.get('publication_year'),
            })

        # move to next page
        cursor = data.get('meta', {}).get('next_cursor')
        if not cursor:  # no more pages
            break
    
    return output

def out_all_doi_and_check_assetId(apikey):
    assets = get_brandeis_asset_doi()

    output = []

    for asset in assets:
        asset_id = None
        has_assetId = False
        asset_id = get_assetID(asset['doi'], apikey)
        if asset_id:
            has_assetId = True
        output.append({
            "openAlex_id": asset['openAlex_id'],
            'doi': asset['doi'],
            'title': asset['title'],
            'publication_year': asset['publication_year'],
            'asset_id': asset_id,
            'has_assetId': has_assetId
        })

    with open(f"sideJobs/output/all_assets.csv", "w", newline="") as csvfile:
        fieldnames = ["openAlex_id", "doi", "title", "publication_year", "asset_id", "has_assetId"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)



# populate_doi_column()



    