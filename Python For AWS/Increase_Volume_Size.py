import boto3

def create_snapshot(volume_id):
    ec2_client = boto3.client('ec2')
    response = ec2_client.create_snapshot(
        VolumeId=volume_id,
        Description='tutorial-volumes-backup'
    )
    return response['SnapshotId']

def modify_volume(volume_id, new_size):
    ec2_client = boto3.client('ec2')
    response = ec2_client.modify_volume(
        VolumeId=volume_id,
        Size=new_size
    )
    return response

def main():
    volume_id = 'your_volume_id_here'  # Replace with your actual volume ID
    new_size = 16  # New size for the volume in GB

    snapshot_id = create_snapshot(volume_id)
    print(f"Snapshot created with ID: {snapshot_id}")

    modify_response = modify_volume(volume_id, new_size)
    print("Volume modification initiated.")
    print(modify_response)

if __name__ == "__main__":
    main()


'''
Before running the script, make sure to replace 'your_volume_id_here' with the actual Volume ID of your data volume. Also, ensure you have the necessary permissions to create snapshots and modify volumes in your AWS account.

This script will create a snapshot of the specified volume and then modify the volume to increase its size to 16 GB. It uses the Boto3 library to interact with AWS services.

'''
