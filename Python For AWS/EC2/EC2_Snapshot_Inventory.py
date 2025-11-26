import boto3
import pandas as pd
from openpyxl import Workbook

def get_snapshot_inventory():
    # Create AWS EC2 client
    ec2_client = boto3.client('ec2')

    # Get all snapshots for the account (owned by 'self')
    response = ec2_client.describe_snapshots(OwnerIds=['self'])
    
    # Prepare list for storing snapshot details
    snapshot_data = []

    for snapshot in response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot['VolumeId']
        creation_date = snapshot['StartTime'].strftime('%Y-%m-%d %H:%M:%S')
        description = snapshot.get('Description', 'No description')

        # Try to get the instance associated with the snapshot (if possible)
        try:
            volume_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
            attachments = volume_response['Volumes'][0].get('Attachments', [])
            instance_id = attachments[0]['InstanceId'] if attachments else 'Not attached'
        except Exception as e:
            instance_id = f"Error fetching instance: {str(e)}"

        snapshot_data.append({
            'Snapshot ID': snapshot_id,
            'Volume ID': volume_id,
            'Instance ID': instance_id,
            'Creation Date': creation_date,
            'Description': description
        })

    # Create DataFrame for easy export
    df = pd.DataFrame(snapshot_data)

    # Save the DataFrame to an Excel file
    output_file = 'snapshot_inventory.xlsx'
    df.to_excel(output_file, index=False)

    print(f"Snapshot inventory has been saved to {output_file}")


if __name__ == '__main__':
    get_snapshot_inventory()
