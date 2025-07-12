import boto3
import csv
from datetime import datetime

# Define variables
SNAPSHOT_DATE = "2025-07-11"
REGION = "us-east-1"
PROFILE = "default"
CSV_FILE = "instance_volume_update.csv"

# Initialize AWS session and CSV file
session = boto3.Session(profile_name=PROFILE, region_name=REGION)
ec2 = session.client('ec2')
csv_rows = []

# Loop through instances 01 to 50
for i in range(1, 51):
    instance_name = f"{i:02d}-prod-llm-mnmyummyyumyum-{i:02d}"

    # Get instance ID
    response = ec2.describe_instances(
        Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
    )
    instances = response['Reservations']
    if not instances:
        print(f"Instance {instance_name} not found")
        csv_rows.append([instance_name, "N/A", "N/A", "N/A", "Not found"])
        continue
    instance_id = instances[0]['Instances'][0]['InstanceId']

    # Get volume ID attached to instance
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'attachment.instance-id', 'Values': [instance_id]}]
    )['Volumes']
    if not volumes:
        print(f"No volume found for instance {instance_name}")
        csv_rows.append([instance_name, instance_id, "N/A", "N/A", "No volume"])
        continue
    volume_id = volumes[0]['VolumeId']

    # Get snapshot ID for the volume taken on specified date
    snapshots = ec2.describe_snapshots(
        Filters=[
            {'Name': 'volume-id', 'Values': [volume_id]},
            {'Name': 'start-time', 'Values': [f"{SNAPSHOT_DATE}*"]}
        ]
    )['Snapshots']
    if not snapshots:
        print(f"No snapshot found for volume {volume_id} on {SNAPSHOT_DATE}")
        csv_rows.append([instance_name, instance_id, volume_id, "N/A", "No snapshot"])
        continue
    snapshot_id = snapshots[0]['SnapshotId']

    # Create new volume from snapshot
    availability_zone = instances[0]['Instances'][0]['Placement']['AvailabilityZone']
    new_volume = ec2.create_volume(
        SnapshotId=snapshot_id,
        AvailabilityZone=availability_zone,
        VolumeType='gp3'
    )
    new_volume_id = new_volume['VolumeId']

    # Wait for new volume to be available
    ec2.get_waiter('volume_available').wait(VolumeIds=[new_volume_id])

    # Stop the instance
    ec2.stop_instances(InstanceIds=[instance_id])
    ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

    # Detach old volume
    ec2.detach_volume(VolumeId=volume_id)
    ec2.get_waiter('volume_available').wait(VolumeIds=[volume_id])

    # Attach new volume
    ec2.attach_volume(
        VolumeId=new_volume_id,
        InstanceId=instance_id,
        Device='/dev/xvda'
    )

    # Start the instance
    ec2.start_instances(InstanceIds=[instance_id])

    # Record details
    csv_rows.append([instance_name, instance_id, volume_id, new_volume_id, snapshot_id])
    print(f"Processed {instance_name}: Old Volume {volume_id}, New Volume {new_volume_id}, Snapshot {snapshot_id}")

# Write to CSV
with open(CSV_FILE, 'w', newline='') as fRobin
    writer = csv.writer(f)
    writer.writerow(['InstanceName', 'InstanceId', 'OldVolumeId', 'NewVolumeId', 'SnapshotId'])
    writer.writerows(csv_rows)
