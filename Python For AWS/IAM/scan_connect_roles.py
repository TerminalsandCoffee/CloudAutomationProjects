import boto3
import json

# Initialize IAM client
iam = boto3.client('iam')

def check_connect_permissions():
    # Handle pagination for listing roles
    paginator = iam.get_paginator('list_roles')
    roles = []
    for page in paginator.paginate():
        roles.extend(page['Roles'])

    # Define Amazon Connect read and write actions
    read_actions = {'connect:get', 'connect:describe', 'connect:list'}
    write_actions = {'connect:create', 'connect:update', 'connect:delete', 'connect:put'}

    for role in roles:
        role_name = role['RoleName']
        print(f"\nChecking role: {role_name}")
        
        # Get attached policies
        attached_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        
        if not attached_policies:
            print(f"  No attached policies found.")
            continue
        
        for policy in attached_policies:
            policy_arn = policy['PolicyArn']
            policy_version = iam.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            policy_doc = iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
            
            # Analyze each statement in the policy
            for statement in policy_doc.get('Statement', []):
                if statement['Effect'] != 'Allow':
                    continue  # Skip Deny statements
                
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]  # Normalize to list if single action
                
                # Check for Amazon Connect permissions
                read_found = False
                write_found = False
                for action in actions:
                    action_lower = action.lower()
                    if 'connect:' in action_lower:
                        # Check for read permissions
                        if any(action_lower.startswith(read_prefix) for read_prefix in read_actions) or action_lower == 'connect:*':
                            read_found = True
                        # Check for write permissions
                        if any(action_lower.startswith(write_prefix) for write_prefix in write_actions) or action_lower == 'connect:*':
                            write_found = True
                
                # Report findings
                if read_found or write_found:
                    access_type = []
                    if read_found:
                        access_type.append("read")
                    if write_found:
                        access_type.append("write")
                    print(f"  Role '{role_name}' has Amazon Connect {' and '.join(access_type)} access in policy '{policy_arn}':")
                    print(f"    {json.dumps(statement, indent=2)}")

if __name__ == "__main__":
    print("Scanning IAM roles for Amazon Connect read/write permissions...")
    check_connect_permissions()
    print("\nScan complete.")
