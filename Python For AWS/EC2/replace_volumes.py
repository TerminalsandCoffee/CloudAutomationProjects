import boto3
import csv
from datetime import datetime
import botocore.exceptions

# === CONFIG ===
SNAPSHOT_DATE = "2025-07-11"
REGION = "us-east-1"
PROFILE = "default"
CSV_FILE = "instance_volume_update.csv"
DRY_RUN = False  # SET TO True FOR TESTING

# === INIT ===
session = boto3.Session(profile_name=PROFILE, region_name=REGION)
ec2 = session.client('ec2')
csv_rows = []

def log_and_append(instance_name, instance_id, volume_id, new_volume_id, snapshot_id, status):
    row = [instance_name, instance_id or "N/A", volume_id or "N/A", new_volume_id or "N/A", snapshot_id or "N/A", status]
    csv_rows.append(row)
    print(f"[LOG] {instance_name}: {status}")

for i in range(1, 51):
    instance_name = f"{i:02d}-prod-llm-mnmyummyyumyum-{i:02d}"

    try:
        # 1. Find instance
        response = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])
        instances = response['Reservations']
        if not instances:
            log_and_append(instance_name, None, None, None, None, "Not found")
            continue
        instance = instances[0]['Instances'][0]
        instance_id = instance['InstanceId']
        az = instance['Placement']['AvailabilityZone']

        # 2. Get root volume
        volumes = ec2.describe_volumes(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance_id]}])['Volumes']
        if not volumes:
            log_and_append(instance_name, instance_id, None, None, None, "No volume")
            continue
        volume_id = volumes[0]['VolumeId']

        # 3. Find snapshot
        snapshots = ec2.describe_snapshots(
            Filters=[
                {'Name': 'volume-id', 'Values': [volume_id]},
                {'Name': 'start-time', 'Values': [f"{SNAPSHOT_DATE}*"]}
            ]
        )['Snapshots']
        if not snapshots:
            log_and_append(instance_name, instance_id, volume_id, None, None, "No snapshot")
            continue
        snapshot_id = snapshots[0]['SnapshotId']

        if DRY_RUN:
            log_and_append(instance_name, instance_id, volume_id, "DRY-RUN-NEW", snapshot_id, "Skipped (dry run)")
            continue

        # 4. Create new volume
        new_volume = ec2.create_volume(SnapshotId=snapshot_id, AvailabilityZone=az, VolumeType='gp3')
        new_volume_id = new_volume['VolumeId']
        ec2.get_waiter('volume_available').wait(VolumeIds=[new_volume_id])

        # 5. Stop, detach, attach, start
        ec2.stop_instances(InstanceIds=[instance_id])
        ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

        ec2.detach_volume(VolumeId=volume_id)
        ec2.get_waiter('volume_available').wait(VolumeIds=[volume_id])

        ec2.attach_volume(VolumeId=new_volume_id, InstanceId=instance_id, Device='/dev/xvda')
        ec2.start_instances(InstanceIds=[instance_id])

        log_and_append(instance_name, instance_id, volume_id, new_volume_id, snapshot_id, "Success")

    except Exception as e:
        log_and_append(instance_name, instance_id or "N/A", volume_id or "N/A", None, None, f"Error: {str(e)}")

# === WRITE CSV ===
with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['InstanceName', 'InstanceId', 'OldVolumeId', 'NewVolumeId', 'SnapshotId', 'Status'])
    writer.writerows(csv_rows)

print(f"\nResults written to {CSV_FILE}")
