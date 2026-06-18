import boto3, json, csv, logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from funder_pipeline.cli.load import register_get_assetID_by_doi, register_link_asset_awards_command, register_link_asset_awards_from_dir_command
from funder_pipeline.cli.maintenance import register_clean_outputs_command
from funder_pipeline.cli.preprocess import register_funder_awards_command, register_unique_funder_command
from funder_pipeline.cli.process import (register_extract_awards_command, register_extract_one_award_command)
from funder_pipeline.handlers.NIH import check_nih_funder
from funder_pipeline.handlers.NSF import check_nsf_funder
from funder_pipeline.handlers.European_Commision import check_eu_commision_funder
from funder_pipeline.stages.extract.fetch_openAlex import get_brandeis_grant
from funder_pipeline.stages.extract.remove_invalid import is_valid_asset

from funder_pipeline.utils.sqs_config import NIH_QUEUE_URL
from funder_pipeline.utils.sqs_config import NSF_QUEUE_URL
from funder_pipeline.utils.sqs_config import EUROPE_RESEARCH_COUNCIL_QUEUE_URL

from funder_pipeline.utils import openAlex_id
import argparse



def process_grant(grant, sqs, queue_url):
    if not grant.get("doi"):
        return "skip_no_doi"

    extract_doi = grant["doi"].split("https://doi.org/")[-1]

    if not is_valid_asset(extract_doi):
        return ("skip_invalid", extract_doi)

    message = {
        "award_id": grant["award_id"],
        "funder_name": grant["funder_name"],
        "doi": extract_doi
    }

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    return "sent"


def log_skipped_doi(doi):
    with open("skipped_dois.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([doi])


def send_grant_sqs_for_one_funder(
    funderId,
    funderName,
    institutionsId="I6902469",
    startyear=2017,
    endYear=2025
):

    sqs = boto3.client("sqs", region_name="us-east-2")

    grants = get_brandeis_grant(funderId, funderName, institutionsId, startyear, endYear)
    print(f"Total grants for {funderName}: {len(grants)}")

    queue_url = get_SQS_URL_by_funder(funderName)
    if not queue_url:
        raise ValueError(f"No queue defined for funder: {funderName}")

    num_skip = 0

    with open(f"sideJobs/invalid_asset/{funderName}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        with ThreadPoolExecutor(max_workers=20) as executor:

            futures = [
                executor.submit(process_grant, grant, sqs, queue_url)
                for grant in grants
            ]

            for future in as_completed(futures):
                result = future.result()

                if isinstance(result, tuple) and result[0] == "skip_invalid":
                    num_skip += 1
                    doi = result[1]

                    writer.writerow([doi])   # write DOI to file

                    print(f"Skipping grant with DOI {doi}. Total skipped: {num_skip}")

    return f"Processed funder: {funderName}"


def get_SQS_URL_by_funder(funderName):
    if check_nih_funder(funderName):
        return NIH_QUEUE_URL
    elif check_nsf_funder(funderName):
        return NSF_QUEUE_URL
    elif check_eu_commision_funder(funderName):
        return EUROPE_RESEARCH_COUNCIL_QUEUE_URL
    return None


# for funderId, funderName in openAlex_id.NIH_FUNDERS.items():
#     send_grant_sqs_for_one_funder(
#         funderId=funderId,
#         funderName=funderName,
#     )

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )

    parser = argparse.ArgumentParser(
        prog="fp",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Research funder ETL pipeline"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    register_unique_funder_command(subparsers)
    register_funder_awards_command(subparsers)
    register_extract_awards_command(subparsers)
    register_extract_one_award_command(subparsers)
    register_link_asset_awards_command(subparsers)
    register_link_asset_awards_from_dir_command(subparsers)
    register_get_assetID_by_doi(subparsers)
    register_clean_outputs_command(subparsers)

    args = parser.parse_args()

    try:
        # Run validation if command has one
        if hasattr(args, "validate_func"):
            args.validate_func(args, parser)

        # Run command
        if hasattr(args, "func"):
            args.func(args)

    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
