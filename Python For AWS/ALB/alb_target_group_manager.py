#!/usr/bin/env python3
"""
ALB Target Group Manager

Manages target registration and deregistration for Application Load Balancer target groups.
Supports bulk operations, draining connections, and health check configuration.

Use Cases:
- Blue-green deployments
- Canary releases
- Maintenance windows
- Auto-scaling integration
- Traffic shifting between environments
"""

import boto3
import argparse
import sys
import time
from typing import List, Dict, Optional

def get_target_group_by_name(elb_client, target_group_name: str) -> Optional[Dict]:
    """
    Find a target group by name.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_name: Name of the target group
        
    Returns:
        Target group dictionary or None if not found
    """
    try:
        response = elb_client.describe_target_groups(Names=[target_group_name])
        if response['TargetGroups']:
            return response['TargetGroups'][0]
        return None
    except elb_client.exceptions.TargetGroupNotFoundException:
        print(f"Target group '{target_group_name}' not found")
        return None
    except Exception as e:
        print(f"Error finding target group: {str(e)}")
        return None

def register_targets(elb_client, target_group_arn: str, targets: List[Dict]) -> bool:
    """
    Register targets with a target group.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        targets: List of target dictionaries with 'Id' and 'Port' keys
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = elb_client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=targets
        )
        print(f"Successfully registered {len(targets)} target(s)")
        return True
    except Exception as e:
        print(f"Error registering targets: {str(e)}")
        return False

def deregister_targets(elb_client, target_group_arn: str, targets: List[Dict], 
                       drain: bool = False) -> bool:
    """
    Deregister targets from a target group.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        targets: List of target dictionaries with 'Id' and 'Port' keys
        drain: If True, wait for connections to drain before completing
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = elb_client.deregister_targets(
            TargetGroupArn=target_group_arn,
            Targets=targets
        )
        print(f"Successfully deregistered {len(targets)} target(s)")
        
        if drain:
            print("Waiting for connections to drain...")
            wait_for_targets_drained(elb_client, target_group_arn, targets)
        
        return True
    except Exception as e:
        print(f"Error deregistering targets: {str(e)}")
        return False

def wait_for_targets_drained(elb_client, target_group_arn: str, targets: List[Dict], 
                             timeout: int = 300, check_interval: int = 10):
    """
    Wait for targets to finish draining connections.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        targets: List of targets being drained
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
    """
    start_time = time.time()
    target_ids = [t['Id'] for t in targets]
    
    while time.time() - start_time < timeout:
        try:
            response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)
            
            all_drained = True
            for target_health in response['TargetHealthDescriptions']:
                target_id = target_health['Target']['Id']
                if target_id in target_ids:
                    state = target_health['TargetHealth']['State']
                    if state != 'draining' and state != 'unused':
                        all_drained = False
                        break
            
            if all_drained:
                print("All targets have finished draining")
                return
            
            time.sleep(check_interval)
        except Exception as e:
            print(f"Error checking drain status: {str(e)}")
            return
    
    print(f"Timeout reached after {timeout} seconds. Some targets may still be draining.")

def get_current_targets(elb_client, target_group_arn: str) -> List[Dict]:
    """
    Get list of currently registered targets.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        
    Returns:
        List of target dictionaries
    """
    try:
        response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)
        targets = []
        for target_health in response['TargetHealthDescriptions']:
            target = target_health['Target']
            targets.append({
                'Id': target['Id'],
                'Port': target['Port']
            })
        return targets
    except Exception as e:
        print(f"Error getting current targets: {str(e)}")
        return []

def update_health_check(elb_client, target_group_arn: str, **kwargs) -> bool:
    """
    Update health check configuration for a target group.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        **kwargs: Health check parameters (Path, IntervalSeconds, TimeoutSeconds, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Only include non-None values
        health_check_params = {k: v for k, v in kwargs.items() if v is not None}
        
        if not health_check_params:
            print("No health check parameters provided")
            return False
        
        response = elb_client.modify_target_group(
            TargetGroupArn=target_group_arn,
            **health_check_params
        )
        print("Health check configuration updated successfully")
        return True
    except Exception as e:
        print(f"Error updating health check: {str(e)}")
        return False

def parse_targets(target_string: str) -> List[Dict]:
    """
    Parse target string into list of target dictionaries.
    Format: "id1:port1,id2:port2" or "id1,id2" (defaults to port 80)
    
    Args:
        target_string: Comma-separated list of targets
        
    Returns:
        List of target dictionaries
    """
    targets = []
    for target_str in target_string.split(','):
        target_str = target_str.strip()
        if ':' in target_str:
            target_id, port = target_str.split(':')
            targets.append({'Id': target_id, 'Port': int(port)})
        else:
            # Default to port 80 if not specified
            targets.append({'Id': target_str, 'Port': 80})
    return targets

def main():
    parser = argparse.ArgumentParser(
        description='Manage ALB Target Groups - Register, deregister, and configure targets'
    )
    parser.add_argument('--target-group', '-tg', required=True,
                       help='Name of the target group')
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register targets')
    register_parser.add_argument('--targets', '-t', required=True,
                                help='Comma-separated targets (format: id1:port1,id2:port2)')
    
    # Deregister command
    deregister_parser = subparsers.add_parser('deregister', help='Deregister targets')
    deregister_parser.add_argument('--targets', '-t', required=True,
                                   help='Comma-separated targets (format: id1:port1,id2:port2)')
    deregister_parser.add_argument('--drain', action='store_true',
                                   help='Wait for connections to drain')
    
    # List command
    subparsers.add_parser('list', help='List current targets')
    
    # Update health check command
    health_parser = subparsers.add_parser('update-health', help='Update health check settings')
    health_parser.add_argument('--path', help='Health check path')
    health_parser.add_argument('--interval', type=int, help='Health check interval (seconds)')
    health_parser.add_argument('--timeout', type=int, help='Health check timeout (seconds)')
    health_parser.add_argument('--healthy-threshold', type=int, help='Healthy threshold count')
    health_parser.add_argument('--unhealthy-threshold', type=int, help='Unhealthy threshold count')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize ELB client
    elb_client = boto3.client('elbv2', region_name=args.region)
    
    # Find target group
    tg = get_target_group_by_name(elb_client, args.target_group)
    if not tg:
        print(f"Target group '{args.target_group}' not found")
        sys.exit(1)
    
    tg_arn = tg['TargetGroupArn']
    print(f"Target Group: {args.target_group}")
    print(f"ARN: {tg_arn}")
    print("")
    
    # Execute command
    if args.command == 'register':
        targets = parse_targets(args.targets)
        register_targets(elb_client, tg_arn, targets)
    
    elif args.command == 'deregister':
        targets = parse_targets(args.targets)
        deregister_targets(elb_client, tg_arn, targets, drain=args.drain)
    
    elif args.command == 'list':
        targets = get_current_targets(elb_client, tg_arn)
        if targets:
            print("Current targets:")
            for target in targets:
                print(f"  - {target['Id']}:{target['Port']}")
        else:
            print("No targets registered")
    
    elif args.command == 'update-health':
        health_params = {}
        if args.path:
            health_params['HealthCheckPath'] = args.path
        if args.interval:
            health_params['HealthCheckIntervalSeconds'] = args.interval
        if args.timeout:
            health_params['HealthCheckTimeoutSeconds'] = args.timeout
        if args.healthy_threshold:
            health_params['HealthyThresholdCount'] = args.healthy_threshold
        if args.unhealthy_threshold:
            health_params['UnhealthyThresholdCount'] = args.unhealthy_threshold
        
        update_health_check(elb_client, tg_arn, **health_params)

if __name__ == "__main__":
    main()

