import boto3
import json
from funderAPI.NIH import check_nih_funder
from funderAPI.NSF import check_nsf_funder
from sideJobs.brandeis_funder import get_brandeis_grant

from utils.sqs_config import NIH_QUEUE_URL
from utils.sqs_config import NSF_QUEUE_URL


def send_grant_sqs_for_one_funder(
    funderId,
    funderName,
    institutionsId="I6902469",
    startyear=2017,
    endYear=2025
):
    """
    funder = {"id": "...", "name": "..."}
    Designed for Airflow dynamic task mapping.
    """


    sqs = boto3.client("sqs", region_name="us-east-2")

    # Get awards for THIS funder only
    grants = get_brandeis_grant(funderId, funderName, institutionsId, startyear, endYear)
    print(f"Total grants for {funderName}: {len(grants)}")

    queue_url = get_SQS_URL_by_funder(funderName)
    if not queue_url:
        raise ValueError(f"No queue defined for funder: {funderName}")

    for grant in grants:
        if not grant.get("doi"):
            continue  # skip if no DOI

        message = {
            "award_id": grant["award_id"],
            "funder_name": grant["funder_name"],
            "doi": grant["doi"].split("https://doi.org/")[-1] if grant["doi"] else None,
        }

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
        # print("Message sent:", response["MessageId"])

    return f"Processed funder: {funderName}"


def get_SQS_URL_by_funder(funderName):
    if check_nih_funder(funderName):
        return NIH_QUEUE_URL
    elif check_nsf_funder(funderName):
        return NSF_QUEUE_URL
   #else if funderName == "NSF":
    return None

# send_grant_sqs_for_one_funder(
#     funderId="f4320306076",
#     funderName="National Science Foundation",
# )