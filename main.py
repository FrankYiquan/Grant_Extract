import boto3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from funderAPI.NIH import check_nih_funder
from funderAPI.NSF import check_nsf_funder
from funderAPI.European_Commision import check_eu_commision_funder
from sideJobs.brandeis_funder import get_brandeis_grant
from sideJobs.remove_invalid import is_valid_asset

from utils.sqs_config import NIH_QUEUE_URL
from utils.sqs_config import NSF_QUEUE_URL
from utils.sqs_config import EUROPE_RESEARCH_COUNCIL_QUEUE_URL

from utils.openAlex_id import NATIONAL_SCIENCE_FOUNDATION


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

    # response = sqs.send_message(
    #     QueueUrl=queue_url,
    #     MessageBody=json.dumps(message)
    # )

    return "sent"


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

    with ThreadPoolExecutor(max_workers=20) as executor:

        futures = [
            executor.submit(process_grant, grant, sqs, queue_url)
            for grant in grants
        ]

        for future in as_completed(futures):
            result = future.result()

            if isinstance(result, tuple) and result[0] == "skip_invalid":
                num_skip += 1
                print(f"Skipping grant with DOI {result[1]}. Total skipped: {num_skip}")

    return f"Processed funder: {funderName}"


def get_SQS_URL_by_funder(funderName):
    if check_nih_funder(funderName):
        return NIH_QUEUE_URL
    elif check_nsf_funder(funderName):
        return NSF_QUEUE_URL
    elif check_eu_commision_funder(funderName):
        return EUROPE_RESEARCH_COUNCIL_QUEUE_URL
    return None


# result = send_grant_sqs_for_one_funder(
#     funderId=NATIONAL_SCIENCE_FOUNDATION,
#     funderName="National Science Foundation",
# )

# print(result)