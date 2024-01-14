import boto3

def remove_version1_tag(ec2_instance_id):
    # Create EC2 client
    ec2_client = boto3.client('ec2')

    # Get current tags for the EC2 instance
    response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [ec2_instance_id]}])
    current_tags = response['Tags']

    # Remove 'version1' from tags
    updated_tags = [{'Key': tag['Key'], 'Value': tag['Value'].replace('version1', '')} for tag in current_tags]

    # Update tags for the EC2 instance
    ec2_client.create_tags(Resources=[ec2_instance_id], Tags=updated_tags)

def scan_and_remove_version1_tags():
    # Create EC2 resource
    ec2_resource = boto3.resource('ec2')

    # Iterate over all EC2 instances in the account
    for instance in ec2_resource.instances.all():
        print(f"Scanning instance: {instance.id}")

        # Check if 'version1' is present in any tag
        version1_found = any('version1' in tag['Key'].lower() or 'version1' in tag['Value'].lower() for tag in instance.tags or [])

        if version1_found:
            print(f"Removing 'version1' tag from instance: {instance.id}")
            remove_version1_tag(instance.id)
        else:
            print("No 'version1' tag found on this instance.")

if __name__ == "__main__":
    scan_and_remove_version1_tags()



'''
This script defines two functions: remove_version1_tag for removing 'version1' from a specific EC2 instance's tags 
&& scan_and_remove_version1_tags for scanning all EC2 instances in the account and removing 'version1' if present.

'''
