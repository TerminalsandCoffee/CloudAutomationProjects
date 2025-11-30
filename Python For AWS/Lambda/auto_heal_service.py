import boto3
import logging
import json

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ssm_client = boto3.client('ssm')
ecs_client = boto3.client('ecs')

def lambda_handler(event, context):
    """
    Triggered by EventBridge when a 5xx error threshold is breached.
    Finds the unhealthy instance and restarts the 'registrator' service via SSM.
    """
    logger.info("Received event: " + json.dumps(event))

    # 1. Parse the Alarm Data (Mock data structure from CloudWatch)
    # In a real scenario, we extract the InstanceId or TargetGroup from the event
    # For this example, we assume the instance ID is passed or looked up via tag
    target_instance_id = "i-0123456789abcdef0"  # Replace with dynamic lookup logic
    service_to_restart = "registrator"

    logger.info(f"Starting remediation for instance: {target_instance_id}")

    try:
        # 2. Execute the restart command on the instance using SSM
        response = ssm_client.send_command(
            InstanceIds=[target_instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': [
                    f"sudo systemctl restart {service_to_restart}",
                    "echo 'Service restarted by Auto-Remediation Lambda'"
                ]
            },
            Comment=f"Auto-healing restart for {service_to_restart}"
        )

        command_id = response['Command']['CommandId']
        logger.info(f"SSM Command sent successfully. Command ID: {command_id}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Remediation initiated for {target_instance_id}")
        }

    except Exception as e:
        logger.error(f"Failed to remediate instance {target_instance_id}: {str(e)}")
        raise e
