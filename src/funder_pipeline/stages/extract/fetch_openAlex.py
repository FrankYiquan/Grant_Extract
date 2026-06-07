import requests
import csv
import pandas as pd
import requests
from funder_pipeline.utils.current_funder import funders
from pathlib import Path


skipped_redflag = [
    "unknown",
    "n/a",
    "none",
    "(nih)",
    "investissements d&apos",
    "in2p3",
    "501100011033"
]

# default institutions Id to Brandeis University 
# end year is not included - so if you want end year to be 2024, do 2025 
# start year is not included - if you want start year to be 2018, do 2017
def get_brandeis_grant(funderId=None, institutionsId="I6902469", startyear=2018,endYear=2024):
    """
    If funderId and funderName are both None → return ALL grants for the university
    If funderId and funderName are provided → return grants for that specific funder
    """
    base_url = "https://api.openalex.org/works"
    startyear = startyear - 1
    endYear = endYear + 1

    # If funderId and funderName BOTH None → do NOT filter by funder
    if funderId == "all":
        filter_str = f"institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"
    else:
        filter_str = f"funders.id:{funderId},institutions.id:{institutionsId},publication_year:>{startyear},publication_year:<{endYear}"

    select_fields = "id,doi,title,publication_year,awards"

    output = []
    cursor = "*"  # initial cursor

    while cursor:
        url = f"{base_url}?filter={filter_str}&select={select_fields}&per-page=200&cursor={cursor}"
        response = requests.get(url)
        data = response.json()

        for asset in data.get("results", []):
            grants = asset.get("awards", [])

            # Case A: No funderId + no funderName → include ALL grants with award_id
            if funderId == "all":
                for grant in grants:
                    award_id = grant.get("funder_award_id")
                    if award_id and not any(flag.lower() in award_id.lower() for flag in skipped_redflag):
                        output.append({
                            "openAlex_id": asset.get("id"),
                            "doi": asset.get("doi"),
                            "title": asset.get("title"),
                            "publication_year": asset.get("publication_year"),
                            "funder_name": grant.get("funder_display_name"),
                            "funder_openAlex_id": grant.get("funder_id").split("https://openalex.org/")[-1],
                            "award_id": grant.get("funder_award_id")
                        })
            # Case B: filter by funderId / funderName            
            else:
                for grant in grants:
                    award_id = grant.get("funder_award_id")
                    grant_openAlex_id = grant.get("funder_id", "").split("https://openalex.org/")[-1]
                    if grant_openAlex_id.lower() == funderId.lower() and award_id and not any(flag.lower() in award_id.lower() for flag in skipped_redflag):
                        output.append({
                            "openAlex_id": asset.get("id"),
                            "doi": asset.get("doi"),
                            "title": asset.get("title"),
                            "publication_year": asset.get("publication_year"),
                            "funder_name": grant.get("funder_display_name"),
                            "funder_openAlex_id": grant.get("funder_id").split("https://openalex.org/")[-1],
                            "award_id": grant.get("funder_award_id")
                        })

        # Move to next page
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

    return output

def export_awards_per_funder(
    funder_id,
    institution_id,
    start_year,
    end_year,
):
    output = get_brandeis_grant(
        funder_id,
        institution_id,
        start_year,
        end_year,
    )

    funder_name = output[0]["funder_name"] if output else "Unknown Funder"

    output_dir = (
        Path("outputs")
        / "award_id"
        / f"{funder_name}_{start_year}_{end_year}_funded_awards.csv"
    )

    with open(output_dir, "w", newline="") as csvfile:
        fieldnames = [
            "openAlex_id",
            "doi",
            "title",
            "publication_year",
            "funder_name",
            "funder_openAlex_id",
            "award_id",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    return funder_name, output_dir, output

def run_award_per_funder(args):
    funder_name, output_dir, _ = export_awards_per_funder(
        args.funder_id,
        args.institutions_id,
        args.start_year,
        args.end_year,
    )

    print(f"Assets and Awards info for {funder_name} exported to {output_dir}")

def run_unique_funder(args):
    """
    This function counts the unique funders for an university within a specified time range and exports the results to a CSV file.
    """
    
    grants = get_brandeis_grant("all", args.institutions_id, args.start_year, args.end_year)

    funder_counts = {}

    for grant in grants:
        funder_id = grant.get("funder_openAlex_id")

        if funder_id not in funder_counts:

            funder_counts[funder_id] = {
                "funder_name": grant.get("funder_name").strip(),
                "funder_openAlex_id": funder_id,
                "count": 1,
                "Is_Implemented": funder_id in funders
            }

        else:
            funder_counts[funder_id]["count"] += 1

    # Convert to sorted list
    result = sorted(
        funder_counts.values(),
        key=lambda x: x["count"],
        reverse=True
    )

    # Create dataframe
    df = pd.DataFrame(result)

    # Export CSV
    output_dir = (
        Path("outputs")
        / "funder_count"
        / f"unique_funders_{args.start_year}_{args.end_year}.csv"
    )
    df.to_csv(output_dir, index=False)

    print(f"Unique funder count exported to {output_dir}")

    return df


