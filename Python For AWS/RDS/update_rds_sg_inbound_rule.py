import boto3

def get_rds_security_groups(rds_endpoints):
    """
    Retrieve a set of VPC security group IDs attached to RDS instances
    whose endpoint addresses match the provided list.
    """
    rds_client = boto3.client('rds', region_name='us-east-1')
    security_groups = set()
    
    # Paginate through all DB instances
    paginator = rds_client.get_paginator('describe_db_instances')
    for page in paginator.paginate():
        for db_instance in page.get('DBInstances', []):
            endpoint = db_instance.get('Endpoint', {}).get('Address', '')
            if endpoint in rds_endpoints:
                print(f"Found matching RDS instance: {db_instance['DBInstanceIdentifier']} with endpoint: {endpoint}")
                for sg_info in db_instance.get('VpcSecurityGroups', []):
                    sg_id = sg_info.get('VpcSecurityGroupId')
                    if sg_id:
                        security_groups.add(sg_id)
    return list(security_groups)

def add_inbound_rule_to_sg(security_group_id, source_sg, port, description):
    """
    Add an inbound rule to the specified security group that allows TCP traffic
    on the given port from the source security group.
    """
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'UserIdGroupPairs': [
                        {
                            'GroupId': source_sg,
                            'Description': description
                        }
                    ]
                }
            ]
        )
        print(f"Successfully added rule to security group {security_group_id}")
    except Exception as e:
        print(f"Error adding rule to security group {security_group_id}: {e}")

def main():
    # List of RDS instance endpoint addresses to search for
    rds_endpoints = [
        "xxx.us-east-1.rds.amazonaws.com",
        "xxx.us-east-1.rds.amazonaws.com"

    ]
    
    # Inbound rule details
    source_sg = "sg-xxx"
    port = 5432
    description = "xxx"
    
    # Retrieve security groups attached to the specified RDS instances
    sg_list = get_rds_security_groups(rds_endpoints)
    print("Security Groups attached to matching RDS instances:", sg_list)
    
    # Add the inbound rule to each security group
    for sg in sg_list:
        add_inbound_rule_to_sg(sg, source_sg, port, description)

if __name__ == "__main__":
    main()
