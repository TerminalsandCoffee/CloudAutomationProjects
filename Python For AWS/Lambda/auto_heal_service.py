import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client("ssm")
ecs = boto3.client("ecs")
elbv2 = boto3.client("elbv2")
ec2 = boto3.client("ec2")

ALLOWED_SOURCE = os.environ.get("EVENT_SOURCE", "aws.cloudwatch")
SSM_DOCUMENT = os.environ.get("SSM_DOCUMENT", "AWS-RunShellScript")
RESTART_COMMANDS = [
    "systemctl restart registrator || service registrator restart",
    "echo auto-healer restarted registrator >> /var/log/auto-healer.log",
]


def lambda_handler(event, context):
    source = event.get("source")
    if source and source != ALLOWED_SOURCE:
        logger.error("Rejected event with unexpected source")
        return {"statusCode": 400, "body": "unexpected event source"}

    cluster_name = os.environ["ECS_CLUSTER_NAME"]
    logger.info("Received EventBridge alarm for auto-heal")

    alarm_name = event["detail"]["alarmName"]
    tg_arn = event["detail"]["configuration"]["metrics"][0]["metricStat"]["metric"]["dimensions"]["TargetGroup"]
    logger.info("Triggered by alarm %s", alarm_name)

    health = elbv2.describe_target_health(TargetGroupArn=tg_arn)
    unhealthy_targets = [
        t
        for t in health["TargetHealthDescriptions"]
        if t["TargetHealth"]["State"] in ("unhealthy", "draining")
        and t["TargetHealth"].get("Reason") in ("Target.FailedHealthChecks", "Target.Deregistered")
    ]

    if not unhealthy_targets:
        logger.info("Verification passed: no unhealthy targets found")
        return {"statusCode": 200, "body": "No unhealthy targets — exiting"}

    instance_ids = set()
    tasks = ecs.list_tasks(cluster=cluster_name, desiredStatus="RUNNING")["taskArns"]
    if not tasks:
        return {"statusCode": 200, "body": "No running tasks"}

    task_details = ecs.describe_tasks(cluster=cluster_name, tasks=tasks)["tasks"]
    unhealthy_ips = {t["Target"]["Id"] for t in unhealthy_targets}

    for task in task_details:
        for attachment in task.get("attachments", []):
            if attachment.get("type") != "ElasticNetworkInterface":
                continue
            eni_id = next((d["value"] for d in attachment["details"] if d["name"] == "networkInterfaceId"), None)
            if not eni_id:
                continue
            eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])["NetworkInterfaces"][0]
            if eni.get("PrivateIpAddress") in unhealthy_ips:
                instance_id = eni.get("Attachment", {}).get("InstanceId")
                if instance_id:
                    instance_ids.add(instance_id)

    if not instance_ids:
        logger.error("Could not map unhealthy targets to EC2 instances")
        return {"statusCode": 500, "body": "Failed to resolve instance IDs"}

    for instance_id in instance_ids:
        try:
            logger.info("Remediating affected host %s", instance_id)
            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=SSM_DOCUMENT,
                TimeoutSeconds=180,
                Parameters={"commands": RESTART_COMMANDS},
                Comment="Auto-Healer: restart registrator",
            )
            logger.info("SSM command %s sent to %s", response["Command"]["CommandId"], instance_id)
        except ClientError as exc:
            logger.error("SSM failed on %s: %s", instance_id, exc)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Auto-Healer completed",
                "remediated_instances": list(instance_ids),
            }
        ),
    }
