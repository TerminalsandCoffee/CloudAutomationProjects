import boto3

def lambda_handler(event, context):
    # Create an EC2 client object
    ec2 = boto3.client('ec2')

    # Get all running instances with the "Environment: Dev" tag
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            },
            {
                'Name': 'tag:Environment',
                'Values': ['Dev']
            }
        ]
    )

    # Stop each instance
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            print(f"Stopping instance {instance['InstanceId']}")
            ec2.stop_instances(InstanceIds=[instance['InstanceId']])