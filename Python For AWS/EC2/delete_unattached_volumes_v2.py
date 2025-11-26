import boto3

def find_unattached_volumes():
    # Create an EC2 client
    ec2 = boto3.client('ec2')

    # Get all volumes
    volumes = ec2.describe_volumes()['Volumes']

    # Filter unattached volumes
    unattached_volumes = [volume for volume in volumes if 'Attachments' not in volume or not volume['Attachments']]

    return unattached_volumes

def delete_unattached_volumes(volumes):
    # Create an EC2 resource
    ec2_resource = boto3.resource('ec2')

    # Delete unattached volumes
    for volume in volumes:
        volume_id = volume['VolumeId']
        try:
            ec2_resource.Volume(volume_id).delete()
            print(f"Volume {volume_id} has been deleted.")
        except Exception as e:
            print(f"Error deleting volume {volume_id}: {str(e)}")

if __name__ == "__main__":
    unattached_volumes = find_unattached_volumes()

    if unattached_volumes:
        print("Unattached volumes found:")
        for volume in unattached_volumes:
            print(f"Volume ID: {volume['VolumeId']}")
        delete_volumes = input("Do you want to delete these volumes? (yes/no): ").lower()

        if delete_volumes == 'yes':
            delete_unattached_volumes(unattached_volumes)
        else:
            print("Deletion canceled. No volumes were deleted.")
    else:
        print("No unattached volumes found.")
