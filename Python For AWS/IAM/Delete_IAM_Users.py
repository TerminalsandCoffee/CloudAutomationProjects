import os
import sys

import boto3

CONFIRM = os.environ.get("CONFIRM_DELETE", "").lower() == "yes"
users_to_delete = [u for u in os.environ.get("IAM_USERS_TO_DELETE", "").split(",") if u]


def delete_iam_user(username):
    iam = boto3.client("iam")
    print(
        "This helper only calls delete_user. Detach keys, MFA, policies, and group "
        "memberships first or the API will fail closed."
    )
    iam.delete_user(UserName=username)
    print(f"IAM user '{username}' deleted successfully.")


if not CONFIRM:
    print("Refusing to delete IAM users. Set CONFIRM_DELETE=yes and IAM_USERS_TO_DELETE.")
    sys.exit(1)

if not users_to_delete:
    print("IAM_USERS_TO_DELETE is empty.")
    sys.exit(1)

for user in users_to_delete:
    delete_iam_user(user)
