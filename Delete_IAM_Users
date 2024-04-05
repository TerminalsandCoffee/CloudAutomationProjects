import boto3

def delete_iam_user(username):
    iam = boto3.client('iam')
    try:
        iam.delete_user(UserName=username)
        print(f"IAM user '{username}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting IAM user '{username}': {str(e)}")

# List of IAM users to delete
users_to_delete = ['test.user1', 'test.user2', 'test.user3']

# Loop through the list and delete each user
for user in users_to_delete:
    delete_iam_user(user)
