import json
import os
from datetime import datetime

import boto3

sqs = boto3.client("sqs")
queue_url = os.environ["QUEUE_URL"]


def lambda_handler(event, context):
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    sqs.send_message(QueueUrl=queue_url, MessageBody=date_time)
    return {
        "statusCode": 200,
        "body": json.dumps(date_time),
    }
