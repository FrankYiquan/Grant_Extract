from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import re, csv

def extract_tag(xml, tag):
    """Extract the content of a specific tag from the given XML string."""

    match = re.search(
        rf"<{tag}>(.*?)</{tag}>",
        xml,
        re.DOTALL
    )
    return match.group(1).strip() if match else None


def count_unique(records, field):
    return len({record.get(field) for record in records if record.get(field)})

def extract_all_awards(awards, start_year, end_year, funder_name):
    """Extract information for all awards by routing them to their appropriate handlers and return the extraction results."""

    successful_awards = [] # awards that are successfully extracted from funder API
    failed_awards = [] # awards where its info can not be found through successfully calling the funder API
    error_awards = [] # awards that when calling the funder API, return an error - for debugging purpose
    award_asset_links = [] # used to link award - asset after importing the successful awards into Espero 
    awards_by_cache_key = defaultdict(list)

    for award in awards:
        cache_key = (
            award["handler"],
            award["award"],
            award["final_funder_name"],
        )
        awards_by_cache_key[cache_key].append(award)

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit one handler call per unique award, then apply that result to
        # every DOI/asset row attached to the award.
        future_to_cache_key = {
            executor.submit(
                handler,
                award_id,
                final_funder_name
            ): cache_key
            for cache_key in awards_by_cache_key
            for handler, award_id, final_funder_name in [cache_key]
        }

        for future in as_completed(future_to_cache_key):
            cache_key = future_to_cache_key[future]
            cached_awards = awards_by_cache_key[cache_key]

            try:
                xml_result = future.result()

                # check whether the extracted award is valid by checking if the amount tag is not empty
                amount = extract_tag(xml_result, "amount")

                if amount in (None, "", "None"):
                    for award in cached_awards:
                        failed_awards.append({
                            "award": award["award"],
                            "doi": award["doi"],   
                            "asset_id": award["asset_id"]
                        })
                else:
                    # since the award id will been through normalization, use the extracted award id as ground truth
                    final_award_id = extract_tag(xml_result, "grantId")
                    for award in cached_awards:
                        # the award is valid and successfully extracted
                        successful_awards.append(xml_result)

                        award_asset_links.append({
                            "award": final_award_id,
                            "doi": award["doi"],
                            "asset_id": award["asset_id"]
                        })

            # record error logs
            except Exception as e:
                for award in cached_awards:
                    error_awards.append({
                        "award": award["award"],
                        "doi": award["doi"],
                        "asset_id": award["asset_id"],
                        "funder_name": award["final_funder_name"],
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    })

    # output extraction logs to csv     
    import_awards_output_dir, failed_awards_output_dir, error_awards_output_dir, award_asset_links_output_dir = output_extraction_logs(
        funder_name, 
        start_year, 
        end_year, 
        successful_awards, 
        failed_awards, 
        error_awards, 
        award_asset_links)
    
    return {
        "success_count": len(successful_awards),
        "failed_count": len(failed_awards),
        "error_count": len(error_awards),
        "success_unique_awards": count_unique(award_asset_links, "award"),
        "success_unique_assets": count_unique(award_asset_links, "asset_id"),
        "failed_unique_awards": count_unique(failed_awards, "award"),
        "failed_unique_assets": count_unique(failed_awards, "asset_id"),
        "error_unique_awards": count_unique(error_awards, "award"),
        "error_unique_assets": count_unique(error_awards, "asset_id"),
        "success_file": import_awards_output_dir,
        "failed_file": failed_awards_output_dir,
        "error_file": error_awards_output_dir,
        "link_file": award_asset_links_output_dir
    }

def output_import_awards_xml(successful_awards, output_dir):
    """Output the successfully extracted awards to an XML file in the required format for Espero import."""

    output_dir = Path(output_dir)

    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<grants xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="schema1.xsd">
'''
    xml_footer = '</grants>'    

    with open(output_dir, 'w', encoding='utf-8') as f:
        f.write(xml_header)

        for award in successful_awards:
            f.write(f"{award}\n")
        f.write(xml_footer)

    return output_dir

def output_extraction_logs(funder_name, start_year, end_year, successful_awards, failed_awards, error_awards, award_asset_links):
    """Output the extraction logs including successful awards, failed awards, error awards and award-asset linking info to separate CSV files for record keeping and later use."""
    
    # 1. output valid, extracted awards to CSV in XML
    import_awards_output_dir = (
        Path("outputs")
        / "import_awards"
        / "success"
        / f"{funder_name}_{start_year}_{end_year}_imported_awards.csv"
    )

    output_import_awards_xml(successful_awards, import_awards_output_dir)
    
    # 2. output valid, extracted awards and thier doi to csv
    # this will be latered used to link the awards with their assets in Espero
    award_asset_links_output_dir = (
        Path("outputs")
        / "award_asset_links"
        / f"{funder_name}_{start_year}_{end_year}_award_asset_links.csv"
    )

    with open(award_asset_links_output_dir, "w", newline="") as csvfile:
        fieldnames = [
            "award",
            "doi",
            "asset_id"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(award_asset_links)

    # 3. output failed awards(awards that unable to get info through funder API but did not raise error) to csv
    failed_awards_output_dir = (
        Path("outputs")
        / "import_awards"
        / "failure"
        / f"{funder_name}_{start_year}_{end_year}_failed_awards.csv"
    )

    with open(failed_awards_output_dir, "w", newline="") as csvfile:
        fieldnames = [
            "award",
            "doi",
            "asset_id"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failed_awards)
    
    # 4. output error awards(awards that raised error when fetching info through funder API) to csv
    error_awards_output_dir = (
        Path("outputs")
        / "import_awards"
        / "error"
        / f"{funder_name}_{start_year}_{end_year}_error_awards.csv"
    )
    
    with open(error_awards_output_dir, "w", newline="") as csvfile:
        fieldnames = [
            "award",
            "doi",
            "asset_id",
            "funder_name",
            "error_type",
            "error_message"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(error_awards)

    return import_awards_output_dir, failed_awards_output_dir, error_awards_output_dir, award_asset_links_output_dir
    
