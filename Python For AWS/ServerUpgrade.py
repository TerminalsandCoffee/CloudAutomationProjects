import boto3

def stop_instance(instance_id):
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter('instance_stopped')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance {instance_id} stopped.")


def create_snapshot(instance_id):
    ec2 = boto3.client('ec2')
    
    # Describe the instance to get the root volume ID
    response = ec2.describe_instances(InstanceIds=[instance_id])
    root_volume_id = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId']
    
    # Create a snapshot of the root volume
    snapshot_response = ec2.create_snapshot(VolumeId=root_volume_id, Description=f'Snapshot for instance {instance_id}')
    
    # Wait for the snapshot to be completed
    snapshot_id = snapshot_response['SnapshotId']
    waiter = ec2.get_waiter('snapshot_completed')
    waiter.wait(SnapshotIds=[snapshot_id])
    
    print(f"Snapshot {snapshot_id} created for instance {instance_id}.")    

def modify_instance_type(instance_id, new_instance_type):
    ec2 = boto3.client('ec2')
    ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='instanceType', Value=new_instance_type)
    print(f"Instance {instance_id} type modified to {new_instance_type}.")

def start_instance(instance_id):
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance {instance_id} started.")

def main():
    instance_id = 'i-enter_your_ID_here'
    new_instance_type = 'Update_to_desired_instance_size'

    stop_instance(instance_id)
    modify_instance_type(instance_id, new_instance_type)
    start_instance(instance_id)

if __name__ == "__main__":
    main()
