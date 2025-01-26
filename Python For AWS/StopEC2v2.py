import boto3

# Specify the region where you want to launch the instances
region = 'us-east-1'

# Specify the AMI ID for the Amazon Linux 2 AMI
ami_id = 'ami-0103f211a154d64a6' 

# Specify the instance type (e.g. t2.micro)
instance_type = 't2.micro'

# Specify the number of instances to launch
num_instances = 3

# Specify the tag key-value pair to tag the instances
tag_key = 'Environment'
tag_value = 'Dev'

# Create an EC2 resource object
ec2 = boto3.resource('ec2', region_name=region)

# Launch the instances
instances = ec2.create_instances(
    ImageId=ami_id,
    InstanceType=instance_type,
    MaxCount=num_instances,
    MinCount=num_instances,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': tag_key,
                    'Value': tag_value
                }
            ]
        }
    ]
)

# Extract the instance IDs from the instances object
instance_ids = [instance.id for instance in instances]

# Start the instances
ec2_client = boto3.client('ec2', region_name=region)
ec2_client.start_instances(InstanceIds=instance_ids)

print('Started instances: ' + ', '.join(instance_ids))


