import requests
import csv

# default institutions Id to Brandeis University # end year is not included - so if you want end year to be 2024, do 2025 # start year is not included - if you want start year to be 2018, do 2017
import requests

def get_brandeis_grant(funderId=None, funderName=None, institutionsId="I6902469", startyear=2017,endYear=2025):
    base_url = "https://api.openalex.org/works"

    # If funderId and funderName BOTH None → do NOT filter by funder
    if funderId == "all" and funderName == "all":
        filter_str = f"institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"
    else:
        filter_str = f"grants.funder:{funderId},institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"

    select_fields = "id,doi,title,publication_year,grants"

    output = []
    cursor = "*"  # initial cursor

    while cursor:
        url = f"{base_url}?filter={filter_str}&select={select_fields}&per-page=200&cursor={cursor}"
        response = requests.get(url)
        data = response.json()

        for asset in data.get("results", []):
            grants = asset.get("grants", [])

            # Case A: No funderId + no funderName → include ALL grants with award_id
            if funderId == "all" and funderName == "all":
                for grant in grants:
                    if grant.get("award_id"):
                        output.append({
                            "openAlex_id": asset.get("id"),
                            "doi": asset.get("doi"),
                            "title": asset.get("title"),
                            "publication_year": asset.get("publication_year"),
                            "funder_name": grant.get("funder_display_name"),
                            "award_id": grant.get("award_id")
                        })
                continue

            # Case B: filter by funderId / funderName
            for grant in grants:
                if grant.get("funder_display_name") == funderName and grant.get("award_id"):
                    output.append({
                        "openAlex_id": asset.get("id"),
                        "doi": asset.get("doi"),
                        "title": asset.get("title"),
                        "publication_year": asset.get("publication_year"),
                        "funder_name": grant.get("funder_display_name"),
                        "award_id": grant.get("award_id")
                    })

        # Move to next page
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

    return output


#output the result to csv
def output_grant_to_csv(funderId, funderName, institutionsId="I6902469", startyear=2017, endYear=2025):
    output = get_brandeis_grant(funderId, funderName, institutionsId, startyear, endYear)

    # write to CSV
    with open(f"sideJobs/output/{funderName}_funded_grant.csv", "w", newline="") as csvfile:
        fieldnames = ["openAlex_id", "doi", "title", "publication_year", "funder_name", "award_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

# To Be Implemented
def get_all_funders(funderId = "all", funderName = "all"):
    return [{}]


# # output_grant_to_csv(funderId="f4320320006", funderName="Royal Society")
# funderName="National Institutes of Health"
# funderId="f4320332161"

# output_grant_to_csv(funderId, funderName)