import boto3

# Initialize Boto3 clients for S3 and IAM
s3_client = boto3.client('s3')
iam_client = boto3.client('iam')

# Get list of S3 buckets
response = s3_client.list_buckets()
buckets = [bucket['Name'] for bucket in response['Buckets']]

# Open a file to write the output
output_file = r'C:\Users\rafael.martinez\Desktop\S3_IAM_Users_List.txt' #You're going to want to change this, you can even make it a .csv
with open(output_file, 'w') as f:
    # Iterate over each bucket
    for bucket in buckets:
        f.write("Bucket: " + bucket + "\n")
        
        # Get list of IAM users
        response = iam_client.list_users()
        users = [user['UserName'] for user in response['Users']]
        
        # Check each IAM user's policies for access to the bucket
        found_users = []
        for user in users:
            try:
                # Check if the IAM user has explicit permissions to the bucket
                s3_client.get_bucket_policy_status(Bucket=bucket)
                found_users.append(user)
            except s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    pass  # No bucket policy found, continue to the next user
                else:
                    raise  # Other error occurred, raise it
                
            # Check if the IAM user has access via an IAM policy
            try:
                response = iam_client.simulate_principal_policy(
                    PolicySourceArn='arn:aws:iam::' + boto3.client('sts').get_caller_identity().get('Account') + ':user/' + user,
                    ActionNames=['s3:GetObject'],
                    ResourceArns=['arn:aws:s3:::' + bucket + '/*']
                )
                if any(res['EvalDecision'] == 'allowed' for res in response['EvaluationResults']):
                    found_users.append(user)
            except iam_client.exceptions.NoSuchEntityException:
                pass  # User doesn't exist, continue to the next user
        
        if found_users:
            f.write("IAM Users with Access:\n")
            for user in found_users:
                f.write(user + "\n")
        else:
            f.write("No IAM users found with access.\n")
        
        f.write("----------------------\n")

print("Output saved to:", output_file)
