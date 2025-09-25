import requests
import csv

# default institutions Id to Brandeis University # end year is not included - so if you want end year to be 2024, do 2025 # start year is not included - if you want start year to be 2018, do 2017
def get_brandeis_grant(funderId, funderName, institutionsId="I6902469", startyear=2017, endYear=2025):
    base_url = "https://api.openalex.org/works"
    filter_str = f"grants.funder:{funderId},institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"
    select_fields = "id,doi,title,publication_year,grants"

    output = []
    cursor = "*"  # initial cursor

    while cursor:
        url = f"{base_url}?filter={filter_str}&select={select_fields}&per-page=200&cursor={cursor}"
        response = requests.get(url)
        data = response.json()

        for asset in data.get('results', []):
            for grant in asset.get('grants', []):
                if grant.get('funder_display_name') == funderName and grant.get('award_id'):
                    output.append({
                        "openAlex_id": asset.get('id'),
                        'doi': asset.get('doi'),
                        'title': asset.get('title'),
                        'publication_year': asset.get('publication_year'),
                        'funder_name': grant.get("funder_display_name"),
                        "award_id": grant.get('award_id')
                    })
                    print("Found award:", grant.get('award_id'))

        # move to next page
        cursor = data.get('meta', {}).get('next_cursor')
        if not cursor:  # no more pages
            break

    # write to CSV
    with open(f"sideJobs/output/{funderName}_funded_grant.csv", "w", newline="") as csvfile:
        fieldnames = ["openAlex_id", "doi", "title", "publication_year", "funder_name", "award_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

get_brandeis_grant(funderId="f4320320006", funderName="Royal Society")
