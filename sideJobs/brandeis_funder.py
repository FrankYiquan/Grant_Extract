

import requests
import csv


import requests
import csv

def get_brandeis_grant():
    base_url = "https://api.openalex.org/works"
    filter_str = "grants.funder:f4320321001,institutions.id:I6902469,publication_year:>2017,publication_year:<2025"
    select_fields = "id,doi,title,publication_year,grants"

    output = []
    cursor = "*"  # initial cursor

    while cursor:
        url = f"{base_url}?filter={filter_str}&select={select_fields}&per-page=200&cursor={cursor}"
        response = requests.get(url)
        data = response.json()

        for asset in data.get('results', []):
            for grant in asset.get('grants', []):
                if grant.get('funder_display_name') == "National Natural Science Foundation of China" and grant.get('award_id'):
                    output.append({
                        "openAlex_id": asset.get('id'),
                        'doi': asset.get('doi'),
                        'title': asset.get('title'),
                        'publication_year': asset.get('publication_year'),
                        'funder_name': grant.get("funder_display_name"),
                        "award_id": grant.get('award_id')
                    })
                    print(grant.get('award_id'))

        # move to next page
        cursor = data.get('meta', {}).get('next_cursor')
        if cursor == "null":  # no more pages
            break

    # write to CSV
    with open("sideJobs/output/nsfc_funded_grant.csv", "w", newline="") as csvfile:
        fieldnames = ["openAlex_id", "doi", "title", "publication_year", "funder_name", "award_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output:
            writer.writerow(row)

get_brandeis_grant()
