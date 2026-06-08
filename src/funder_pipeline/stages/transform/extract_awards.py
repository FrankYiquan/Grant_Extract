from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import re, csv

def extract_tag(xml, tag):
    """Extract the content of a specific tag from the given XML string."""

    match = re.search(
        rf"<{tag}>(.*?)</{tag}>",
        xml,
        re.DOTALL
    )
    return match.group(1).strip() if match else None

def extract_all_awards(awards, start_year, end_year, funder_name):
    """Extract information for all awards by routing them to their appropriate handlers and return the extraction results."""

    successful_awards = []
    failed_awards = []
    error_awards = []
    award_asset_links = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        # submit all awards to their respective handlers and collect the futures
        future_to_award = {
            executor.submit(
                award["handler"],
                award["award"],
                award["final_funder_name"]
            ): award
            for award in awards
        }

        for future in as_completed(future_to_award):
            award = future_to_award[future]

            try:
                xml_result = future.result()

                # check whether the extracted award is valid by checking if the amount tag is not empty
                amount = extract_tag(xml_result, "amount")

                if amount in (None, "", "None"):
                    failed_awards.append({
                        "award": award["award"],
                        "doi": award["doi"],   
                    })
                else:
                    # the award is valid and successfully extracted
                    successful_awards.append(xml_result)

                    # since the award id will been through normalization, use the extracted award id as ground truth
                    final_award_id = extract_tag(xml_result, "grantId")
                    award_asset_links.append({
                        "award": final_award_id,
                        "doi": award["doi"],
                    })

            # record error logs
            except Exception as e:
                error_awards.append({
                    "award": award["award"],
                    "funder_name": award["final_funder_name"],
                    "doi": award["doi"],   
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
        "success_file": import_awards_output_dir,
        "failed_file": failed_awards_output_dir,
        "error_file": error_awards_output_dir,
        "link_file": award_asset_links_output_dir
    }

def output_extraction_logs(funder_name, start_year, end_year, successful_awards, failed_awards, error_awards, award_asset_links):
    """Output the extraction logs including successful awards, failed awards, error awards and award-asset linking info to separate CSV files for record keeping and later use."""
    
    # 1. output valid, extracted awards to CSV in XML
    import_awards_output_dir = (
        Path("outputs")
        / "import_awards"
        / "success"
        / f"{funder_name}_{start_year}_{end_year}_imported_awards.csv"
    )

    # required XML format for Espero import
    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<grants xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="schema1.xsd">
'''
    xml_footer = '</grants>'

    with open(import_awards_output_dir, 'w', encoding='utf-8') as f:
        f.write(xml_header)

        for award in successful_awards:
            f.write(f"{award}\n")
        f.write(xml_footer)
    
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
            "funder_name",
            "error_type",
            "error_message"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(error_awards)

    return import_awards_output_dir, failed_awards_output_dir, error_awards_output_dir, award_asset_links_output_dir
    


