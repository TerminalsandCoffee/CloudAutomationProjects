import boto3

# AWS credentials and region
aws_access_key_id = 'YOUR_ACCESS_KEY'
aws_secret_access_key = 'YOUR_SECRET_KEY'
aws_region = 'YOUR_REGION'

# IAM group and S3 bucket information
iam_group_name = 'TestGroup'
s3_bucket_name = 'rafsautomation'

# Users to be added to the IAM group
test_users = ['user1', 'user2', 'user3', 'user4', 'user5']

# Create an IAM client
iam_client = boto3.client('iam', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

# Create the IAM group if it doesn't exist
try:
    iam_client.create_group(GroupName=iam_group_name)
except iam_client.exceptions.EntityAlreadyExistsException:
    print(f"IAM group '{iam_group_name}' already exists.")

# Add users to the IAM group
for user in test_users:
    try:
        iam_client.add_user_to_group(GroupName=iam_group_name, UserName=user)
        print(f"User '{user}' added to IAM group '{iam_group_name}'.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"IAM group '{iam_group_name}' does not exist.")

# Create an S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

# Define the policy to grant access to the S3 bucket
s3_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": f"arn:aws:s3:::{s3_bucket_name}/*"
        }
    ]
}

# Attach the policy to the IAM group
iam_client.put_group_policy(GroupName=iam_group_name, PolicyName='S3AccessPolicy', PolicyDocument=str(s3_policy))

print(f"Policy attached to IAM group '{iam_group_name}' granting access to S3 bucket '{s3_bucket_name}'.")
