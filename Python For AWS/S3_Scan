import boto3

# Set your AWS credentials
aws_access_key_id = 'YOUR_ACCESS_KEY_ID'
aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'

# Set the S3 bucket name
bucket_name = 'YOUR_BUCKET_NAME'

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Initialize the S3 client
s3 = session.client('s3')

# List all objects in the bucket
response = s3.list_objects_v2(Bucket=bucket_name)

if 'Contents' in response:
    for obj in response['Contents']:
        object_key = obj['Key']
        object_response = s3.get_object(Bucket=bucket_name, Key=object_key)
        object_data = object_response['Body'].read().decode('utf-8')

        # Add your sensitive data checks here
        # Example: Check for Social Security Numbers
        if 'SSN' in object_data:
            print(f"S3 Object with key {object_key} contains sensitive data.")

        # Add more checks as needed

else:
    print("No objects found in the bucket.")
