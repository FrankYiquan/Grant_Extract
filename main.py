import boto3
import json

from funderAPI.NIH import check_nih_funder
from sideJobs.brandeis_funder import get_brandeis_grant




def send_grant_sqs(funderId, funderName, institutionsId="I6902469", startyear=2017, endYear=2025):

    sqs = boto3.client("sqs", region_name="us-east-2")  
    NIH_Queue_URL = "https://sqs.us-east-2.amazonaws.com/050752631001/NIH-Queue"
    SQS_URL = None

    #get all the grant associate with the funder name and institution Id
    grants = get_brandeis_grant(funderId, funderName, institutionsId, startyear, endYear) #an array

    if check_nih_funder(funderName):
        SQS_URL = NIH_Queue_URL

    # elif ....:
    #      SQS_URL = "other queue url"


    for grant in grants:
        message = {
            "award_id": grant['award_id'],
            "funder_name": funderName
        }

        response = sqs.send_message(
            QueueUrl=SQS_URL,
            MessageBody=json.dumps(message)
        )

        print("Message sent:", response["MessageId"])


# send_grant_sqs(funderId="f4320332161", funderName="National Institutes of Health")



# funderName="National Institutes of Health"
# result = check_nih_funder(funderName)
# print(result)





   