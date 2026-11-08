import os

import boto3

bucket_name = os.environ["S3_BUCKET_NAME"]

s3 = boto3.client("s3")

response = s3.list_objects_v2(Bucket=bucket_name)

if "Contents" not in response:
    print("No objects found in the bucket.")
else:
    for obj in response["Contents"]:
        object_key = obj["Key"]
        object_response = s3.get_object(Bucket=bucket_name, Key=object_key)
        object_data = object_response["Body"].read().decode("utf-8", errors="replace")
        if "SSN" in object_data:
            print(f"S3 Object with key {object_key} contains sensitive data.")
