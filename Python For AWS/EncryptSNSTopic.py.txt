import boto3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_unencrypted_sns_topics():
    sns_client = boto3.client("sns")
    topics = []
    
    try:
        paginator = sns_client.get_paginator("list_topics")
        for page in paginator.paginate():
            for topic in page.get("Topics", []):
                topic_arn = topic["TopicArn"]
                attributes = sns_client.get_topic_attributes(TopicArn=topic_arn)["Attributes"]
                
                if "KmsMasterKeyId" not in attributes or not attributes["KmsMasterKeyId"]:
                    topics.append(topic_arn)
        
        logger.info(f"Found {len(topics)} unencrypted topics.")
    except Exception as e:
        logger.error(f"Error retrieving SNS topics: {e}")
    
    return topics

def enable_encryption_for_topic(topic_arn):
    sns_client = boto3.client("sns")
    kms_key = "alias/aws/sns"
    
    try:
        sns_client.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName="KmsMasterKeyId",
            AttributeValue=kms_key
        )
        logger.info(f"Encryption enabled for topic: {topic_arn}")
    except Exception as e:
        logger.error(f"Error enabling encryption for topic {topic_arn}: {e}")

def main():
    logger.info("Starting encryption process for SNS topics...")
    unencrypted_topics = get_unencrypted_sns_topics()
    
    if not unencrypted_topics:
        logger.info("No unencrypted topics found.")
        return
    
    for topic in unencrypted_topics:
        enable_encryption_for_topic(topic)

if __name__ == "__main__":
    main()