import os

import boto3
from botocore.exceptions import ClientError

MAX_INSTANCES = int(os.environ.get("MAX_INSTANCES", "10"))
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"
ENVIRONMENT = os.environ.get("TARGET_ENVIRONMENT", "Dev")


def lambda_handler(event, context):
    ec2 = boto3.client("ec2")

    instances = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "tag:Environment", "Values": [ENVIRONMENT]},
        ]
    )

    instance_ids = [
        instance["InstanceId"]
        for reservation in instances["Reservations"]
        for instance in reservation["Instances"]
    ][:MAX_INSTANCES]

    if not instance_ids:
        print("No matching instances.")
        return {"stopped": [], "dry_run": DRY_RUN}

    print(f"{'Would stop' if DRY_RUN else 'Stopping'} {instance_ids}")
    try:
        ec2.stop_instances(InstanceIds=instance_ids, DryRun=DRY_RUN)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if DRY_RUN and code == "DryRunOperation":
            return {"stopped": instance_ids, "dry_run": True}
        raise

    return {"stopped": instance_ids, "dry_run": DRY_RUN}
