import boto3


#service resource
sqs = boto3.resource('sqs', region_name='us-east-1')

#creates the queue, and returns an SQS.Queue instance
queue = sqs.create_queue(QueueName='OrderTracker')

#URL that will be needed for our next code. 
print(queue.url)
