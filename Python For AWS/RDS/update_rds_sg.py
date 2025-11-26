#!/usr/bin/env python3
import boto3
import time
import sys

# Source security group to add to inbound rules
SOURCE_SG_ID = 'sg-xxx'
# Port for the PostgreSQL
PORT = 5432
# Description for the rule
DESCRIPTION = 'xxx'

# List of RDS endpoints to process
RDS_ENDPOINTS = [
    'xxx.rds.amazonaws.com',
    'xxx.us-east-1.rds.amazonaws.com'
]

def get_db_identifier(endpoint):
    """Extract the database identifier from an RDS endpoint."""
    if '.cluster-' in endpoint:
        # This is an Aurora cluster
        return endpoint.split('.cluster-')[0]
    else:
        # Regular RDS instance
        return endpoint.split('.')[0]

def locate_rds_and_security_groups():
    """Find all RDS instances and their associated security groups."""
    rds_client = boto3.client('rds')
    results = []
    
    print(f"Looking up security groups for {len(RDS_ENDPOINTS)} RDS instances...")
    
    for endpoint in RDS_ENDPOINTS:
        print(f"\nProcessing: {endpoint}")
        db_id = get_db_identifier(endpoint)
        
        # Try to find as regular instance first
        try:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_id)
            if response['DBInstances']:
                instance = response['DBInstances'][0]
                sg_ids = [sg['VpcSecurityGroupId'] for sg in instance.get('VpcSecurityGroups', [])]
                if sg_ids:
                    print(f"  Found security groups: {', '.join(sg_ids)}")
                    results.append({
                        'endpoint': endpoint,
                        'identifier': db_id,
                        'type': 'instance',
                        'security_groups': sg_ids
                    })
                else:
                    print(f"  ⚠️ No security groups found for {endpoint}")
                continue
        except rds_client.exceptions.DBInstanceNotFoundFault:
            pass  # Not found as instance, will try as cluster
        except Exception as e:
            print(f"  ❌ Error looking up instance {db_id}: {str(e)}")
        
        # Try to find as Aurora cluster
        try:
            response = rds_client.describe_db_clusters(DBClusterIdentifier=db_id)
            if response['DBClusters']:
                cluster = response['DBClusters'][0]
                sg_ids = [sg['VpcSecurityGroupId'] for sg in cluster.get('VpcSecurityGroups', [])]
                if sg_ids:
                    print(f"  Found security groups for cluster: {', '.join(sg_ids)}")
                    results.append({
                        'endpoint': endpoint,
                        'identifier': db_id,
                        'type': 'cluster',
                        'security_groups': sg_ids
                    })
                else:
                    print(f"  ⚠️ No security groups found for cluster {endpoint}")
                continue
        except rds_client.exceptions.DBClusterNotFoundFault:
            print(f"  ❌ Could not find RDS instance or cluster for {endpoint}")
        except Exception as e:
            print(f"  ❌ Error looking up cluster {db_id}: {str(e)}")
    
    return results

def update_security_group(sg_id):
    """Add the source security group to the inbound rules of the target security group."""
    ec2_client = boto3.client('ec2')
    
    try:
        # Check if rule already exists
        response = ec2_client.describe_security_groups(GroupIds=[sg_id])
        sg = response['SecurityGroups'][0]
        
        # Check existing rules
        for rule in sg['IpPermissions']:
            if rule.get('FromPort') == PORT and rule.get('ToPort') == PORT and rule.get('IpProtocol') == 'tcp':
                for pair in rule.get('UserIdGroupPairs', []):
                    if pair.get('GroupId') == SOURCE_SG_ID:
                        print(f"  Rule already exists in security group {sg_id}")
                        return False
        
        # Add the new rule
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': PORT,
                    'ToPort': PORT,
                    'UserIdGroupPairs': [
                        {
                            'GroupId': SOURCE_SG_ID,
                            'Description': DESCRIPTION
                        }
                    ]
                }
            ]
        )
        print(f"  ✅ Successfully added inbound rule to security group {sg_id}")
        return True
    except Exception as e:
        print(f"  ❌ Error updating security group {sg_id}: {str(e)}")
        return False

def main():
    print("RDS Security Group Updater")
    print("=========================")
    print(f"Source Security Group: {SOURCE_SG_ID}")
    print(f"Port: {PORT}")
    print(f"Description: {DESCRIPTION}")
    print("=========================")
    
    # Verify AWS credentials
    try:
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()["Account"]
        print(f"Using AWS Account: {account_id}\n")
    except Exception as e:
        print(f"❌ Error with AWS credentials: {str(e)}")
        print("Please ensure AWS credentials are configured correctly.")
        sys.exit(1)
    
    # Step 1: Find all RDS instances and their security groups
    rds_info = locate_rds_and_security_groups()
    
    if not rds_info:
        print("\n❌ No RDS instances found. Please check the endpoint list.")
        sys.exit(1)
    
    # Step 2: Add the source security group to each target security group
    print("\nUpdating security group inbound rules...")
    
    success_count = 0
    processed_sgs = set()  # Track processed security groups to avoid duplicates
    
    for rds in rds_info:
        print(f"\nWorking on {rds['endpoint']}")
        for sg_id in rds['security_groups']:
            if sg_id in processed_sgs:
                print(f"  Security group {sg_id} already processed, skipping")
                continue
                
            processed_sgs.add(sg_id)
            
            print(f"  Updating security group: {sg_id}")
            if update_security_group(sg_id):
                success_count += 1
            
            # Small delay to avoid throttling
            time.sleep(0.5)
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total RDS endpoints processed: {len(RDS_ENDPOINTS)}")
    print(f"RDS instances/clusters found: {len(rds_info)}")
    print(f"Unique security groups processed: {len(processed_sgs)}")
    print(f"Successfully updated security groups: {success_count}")
    print("===============")
    
if __name__ == "__main__":
    main()
