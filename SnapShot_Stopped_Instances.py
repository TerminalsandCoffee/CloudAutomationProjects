import boto3

# Initialize Boto3 EC2 client
ec2_client = boto3.client('ec2')

# List of stopped instance IDs
stopped_instance_ids = [
    'i-123holleratme',
    # Add more instance IDs as needed
]

# Function to create snapshots of volumes attached to stopped instances
def create_snapshots(instance_ids):
    for instance_id in instance_ids:
        try:
            # Describe instances to get volume information
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            reservations = response['Reservations']
            for reservation in reservations:
                for instance in reservation['Instances']:
                    for block_device in instance['BlockDeviceMappings']:
                        volume_id = block_device['Ebs']['VolumeId']
                        # Create snapshot
                        snapshot_response = ec2_client.create_snapshot(
                            VolumeId=volume_id,
                            Description=f'Snapshot for terminated instance {instance_id}'
                        )
                        snapshot_id = snapshot_response['SnapshotId']
                        print(f'Snapshot created for volume {volume_id}: {snapshot_id}')
        except Exception as e:
            print(f'Error creating snapshots for instance {instance_id}: {str(e)}')

# Call function to create snapshots
create_snapshots(stopped_instance_ids)
