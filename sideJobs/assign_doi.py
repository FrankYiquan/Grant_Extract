import requests
import pandas as pd

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

# populate_doi_column()


    