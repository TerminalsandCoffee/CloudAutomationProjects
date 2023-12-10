import boto3

def stop_instance(instance_id):
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter('instance_stopped')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance {instance_id} stopped.")

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
