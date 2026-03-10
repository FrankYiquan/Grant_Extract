import boto3
import json
import csv

from concurrent.futures import ThreadPoolExecutor, as_completed

from funderAPI.NIH import check_nih_funder
from funderAPI.NSF import check_nsf_funder
from funderAPI.European_Commision import check_eu_commision_funder
from sideJobs.brandeis_funder import get_brandeis_grant
from sideJobs.remove_invalid import is_valid_asset

from utils.sqs_config import NIH_QUEUE_URL
from utils.sqs_config import NSF_QUEUE_URL
from utils.sqs_config import EUROPE_RESEARCH_COUNCIL_QUEUE_URL

from utils import openAlex_id


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


# for funderId, funderName in openAlex_id.NSF_FUNDERS.items():
#     send_grant_sqs_for_one_funder(
#         funderId=funderId,
#         funderName=funderName,
#     )