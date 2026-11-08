import os
from datetime import datetime

import boto3

region_name = os.environ.get("AWS_REGION", "us-east-2")
bucket_name = os.environ["ELB_LOG_BUCKET"]
prefix = os.environ.get("ELB_LOG_PREFIX", "")
start_time = datetime.fromisoformat(os.environ["LOG_START_UTC"])
end_time = datetime.fromisoformat(os.environ["LOG_END_UTC"])

s3 = boto3.client("s3", region_name=region_name)

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

for obj in response.get("Contents", []):
    key = obj["Key"]
    timestamp_str = key.split("/")[-1].split(".")[1]
    timestamp = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%S")
    if start_time <= timestamp <= end_time:
        filename = key.split("/")[-1]
        s3.download_file(bucket_name, key, filename)
        print(f"Downloaded: {filename}")
