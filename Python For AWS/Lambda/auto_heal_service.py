import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm      = boto3.client('ssm')
ecs      = boto3.client('ecs')
elbv2    = boto3.client('elbv2')
ec2      = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    logger.info(f"EventBridge event: {json.dumps(event)}")

    # 1. Parse the CloudWatch alarm that EventBridge forwarded
    alarm_name = event['detail']['alarmName']
    tg_arn = event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['TargetGroup']
    logger.info(f"Triggered by alarm '{alarm_name}' for TargetGroup {tg_arn}")

    # 2. THE "VERIFY" PHASE — double-check there really are unhealthy targets
    health = elbv2.describe_target_health(TargetGroupArn=tg_arn)
    unhealthy_targets = [
        t for t in health['TargetHealthDescriptions']
        if t['TargetHealth']['State'] in ('unhealthy', 'draining')
           and t['TargetHealth'].get('Reason') in ('Target.FailedHealthChecks', 'Target.Deregistered')
    ]

    if not unhealthy_targets:
        logger.info("Verification passed: no unhealthy targets found — nothing to do")
        return {'statusCode': 200, 'body': 'No unhealthy targets — exiting'}

    logger.warning(f"Verification failed: {len(unhealthy_targets)} unhealthy targets detected")

    # 3. Resolve unhealthy tasks → container instances → EC2 instance IDs
    instance_ids = set()

    # Get all running tasks in the cluster (you can make cluster name dynamic or pass via alarm tags)
    cluster_name = 'production-ecs-cluster'  # or extract from alarm tags in real life
    tasks = ecs.list_tasks(cluster=cluster_name, desiredStatus='RUNNING')['taskArns']

    task_details = ecs.describe_tasks(cluster=cluster_name, tasks=tasks)['tasks']

    for target in unhealthy_targets:
        target_ip   = target['Target']['Id']      # this is the task private IP
        target_port = target['Target']['Port']

        for task in task_details:
            for container in task['containers']:
                if any(net['networkInterfaceId'] for net in container.get('networkInterfaces', [])):
                    # Very fast approximate match — in prod I used exact IP+port lookup via ENI tags
                    for attachment in task['attachments']:
                        if attachment['type'] == 'ElasticNetworkInterface':
                            eni_id = next((d['value'] for d in attachment['details']
                                          if d['name'] == 'networkInterfaceId'), None)
                            if eni_id:
                                eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])['NetworkInterfaces'][0]
                                if eni.get('PrivateIpAddress') == target_ip:
                                    instance_ids.add(eni['Attachment']['InstanceId'])

    if not instance_ids:
        logger.error("Could not map unhealthy targets to EC2 instances")
        return {'statusCode': 500, 'body': 'Failed to resolve instance IDs'}

    # 4. THE "PROTECT" PHASE — surgical restart of registrator only on affected hosts
    service_name = "registrator"
    restart_cmd = f"sudo systemctl restart {service_name} || sudo service {service_name} restart"

    for instance_id in instance_ids:
        try:
            logger.info(f"Remediating affected host {instance_id}")
            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                TimeoutSeconds=180,
                Parameters={
                    'commands': [
                        restart_cmd,
                        f"echo '[$(date)] Auto-Healer restarted {service_name} due to stale routes' >> /var/log/auto-healer.log"
                    ]
                },
                Comment="Auto-Healer: restarting registrator due to stale-route 5xx errors"
            )
            cmd_id = response['Command']['CommandId']
            logger.info(f"SSM command {cmd_id} sent to {instance_id}")

        except ClientError as e:
            logger.error(f"SSM failed on {instance_id}: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Auto-Healer completed',
            'remediated_instances': list(instance_ids)
        })
    }
