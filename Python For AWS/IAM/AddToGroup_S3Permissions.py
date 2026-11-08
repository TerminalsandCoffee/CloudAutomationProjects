import json
import os

import boto3

# Use the default credential chain (profile, instance role, or env). Do not hardcode keys.
iam_group_name = os.environ.get("IAM_GROUP_NAME", "TestGroup")
s3_bucket_name = os.environ["S3_BUCKET_NAME"]
s3_prefix = os.environ.get("S3_PREFIX", "")
test_users = [u for u in os.environ.get("IAM_USER_NAMES", "").split(",") if u]

iam_client = boto3.client("iam")

try:
    iam_client.create_group(GroupName=iam_group_name)
except iam_client.exceptions.EntityAlreadyExistsException:
    print(f"IAM group '{iam_group_name}' already exists.")

for user in test_users:
    try:
        iam_client.add_user_to_group(GroupName=iam_group_name, UserName=user)
        print(f"User '{user}' added to IAM group '{iam_group_name}'.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"User '{user}' does not exist; skipped.")

object_arn = f"arn:aws:s3:::{s3_bucket_name}/{s3_prefix}*" if s3_prefix else f"arn:aws:s3:::{s3_bucket_name}/*"
s3_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": f"arn:aws:s3:::{s3_bucket_name}",
        },
        {
            "Sid": "ReadWritePrefix",
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
            "Resource": object_arn,
        },
    ],
}

iam_client.put_group_policy(
    GroupName=iam_group_name,
    PolicyName="S3AccessPolicy",
    PolicyDocument=json.dumps(s3_policy),
)

print(f"Least-privilege object policy attached to IAM group '{iam_group_name}'.")
