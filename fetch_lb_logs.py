import boto3
from datetime import datetime

# AWS credentials and region
aws_access_key_id = 'your_access_key_id'
aws_secret_access_key = 'your_secret_access_key'
region_name = 'us-east-2'

# S3 bucket and prefix
bucket_name = 'account#-us-east-1-elb-logs'
prefix = 'enterS3filepath'

# Timeframe for logs (in UTC)
start_time = datetime(2024, 2, 27, 15, 0, 0)  # 3pm UTC
end_time = datetime(2024, 2, 27, 22, 0, 0)    # 5pm UTC

# Connect to S3
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=region_name)

# List objects in the bucket with the given prefix
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

# Download logs within the specified timeframe
for obj in response.get('Contents', []):
    key = obj['Key']
    timestamp_str = key.split('/')[-1].split('.')[1]  # Extract timestamp from key
    timestamp = datetime.strptime(timestamp_str, '%Y%m%dT%H%M%S')
    if start_time <= timestamp <= end_time:
        filename = key.split('/')[-1]
        s3.download_file(bucket_name, key, filename)
        print(f"Downloaded: {filename}")
