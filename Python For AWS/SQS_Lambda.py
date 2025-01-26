import json
import boto3
from datetime import datetime

# Create SQS client and get queue URL
sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/397758027793/OrderTracker'

def lambda_handler(event, context):
    # Get the current time as a formatted string
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    
    # Send the message to the queue
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=date_time)
    
    # Return a response
    return {
        'statusCode': 200,
        'body': json.dumps(date_time)
    }

#made change to the above code.