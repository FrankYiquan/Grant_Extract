from concurrent.futures import ThreadPoolExecutor
from funder_pipeline.utils.current_funder import funders
import re
from pathlib import Path
import csv


def matches_rule(award: str, config: dict) -> bool:
    """Check if the given award matches any of the rules in the config.
    The rules include:
    - prefixes: if the award starts with any of the prefixes
    - keywords: if the award contains any of the keywords (case-insensitive)
    - regex: if the award matches any of the regex patterns
    """
    if any(award.startswith(p) for p in config.get("prefixes", [])):
        return True

    award_upper = award.upper()

    if any(k.upper() in award_upper for k in config.get("keywords", [])):
        return True

    if any(re.search(r, award) for r in config.get("regex", [])):
        return True

    return False

def route_single_award_to_handler(funder_id: str, award: str):
    """Given a funder_id and an award, determine the appropriate handler for the award based on the routing rules defined in the funders config.
    """
    funder = funders.get(funder_id)

    if not funder:
        return None

    initial_handler = funder["handler"]
    final_handler = initial_handler
    final_funder_name = funder["name"]
    final_funder_id = funder_id

    for id, config in funders.items():
        if matches_rule(award, config):
            if config["handler"] != initial_handler:
                final_handler = config["handler"]
                final_funder_name = config["name"]
                final_funder_id = id

    return final_handler, final_funder_name, final_funder_id

def process_award(award, funder_id, funder_name):
    """Process a single award by routing it to the appropriate handler and returning the routing outcome."""
    handler, final_funder_name, final_funder_id = (
        route_single_award_to_handler(
            funder_id,
            award["award"]
        )
    )

    return {
        "award": award["award"],
        "initial_funder_id": funder_id,
        "initial_funder_name": funder_name,
        "final_funder_name": final_funder_name,
        "final_funder_id": final_funder_id,
        "handler": handler,
        "change_handler": funder_id != final_funder_id,
    }

def route_all_awards_to_handlers(awards: list, funder_id: str, funder_name: str, start_year: int, end_year: int):
    """Route all awards to their appropriate handlers based on the routing rules defined in the funders config. The routing results are saved to a CSV file."""
    with ThreadPoolExecutor(max_workers=20) as executor:
        routing_results = list(executor.map(
            lambda award: process_award(award, funder_id, funder_name),
            awards        
        ))
    
    routing_outcome_output_dir = (
        Path("outputs")
        / "routing_outcomes"
        / f"{funder_name}_{start_year}_{end_year}_routing_outcomes.csv"
    )

    with open(routing_outcome_output_dir, "w", newline="") as csvfile:
        fieldnames = [
            "award",
            "initial_funder_id",
            "initial_funder_name",
            "final_funder_name",
            "final_funder_id",
            "handler",
            "change_handler"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(routing_results)

    return routing_results, routing_outcome_output_dir