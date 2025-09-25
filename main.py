import boto3
import json

sqs = boto3.client("sqs", region_name="us-east-1")  # change to your region
NIH_Queue_URL = "https://sqs.us-east-2.amazonaws.com/050752631001/NIH-Queue"

message = {
    "award_id": "U19AG051426",
    "funder_name": "NIH"
}

response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps(message)
)

print("Message sent:", response["MessageId"])
