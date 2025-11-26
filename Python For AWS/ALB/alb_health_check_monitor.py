#!/usr/bin/env python3
"""
ALB Health Check Monitor

Monitors target health across all Application Load Balancers and target groups.
Generates reports on unhealthy targets and can optionally send notifications.

Use Cases:
- Proactive monitoring of application health
- Automated alerting for unhealthy targets
- Health check compliance reporting
- Integration with monitoring systems
"""

import boto3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Use environment variables or default credential chain
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
SNS_TOPIC_ARN = os.environ.get('ALB_HEALTH_SNS_TOPIC_ARN', None)  # Optional SNS topic for alerts

def get_all_alb_target_groups(elb_client) -> List[Dict]:
    """
    Retrieve all target groups for Application Load Balancers.
    
    Returns:
        List of target group dictionaries
    """
    target_groups = []
    paginator = elb_client.get_paginator('describe_target_groups')
    
    try:
        for page in paginator.paginate():
            for tg in page['TargetGroups']:
                # Filter for ALB target groups (not NLB or CLB)
                if tg['TargetType'] in ['instance', 'ip']:
                    target_groups.append(tg)
    except Exception as e:
        print(f"Error retrieving target groups: {str(e)}")
        raise
    
    return target_groups

def get_target_health(elb_client, target_group_arn: str) -> Dict:
    """
    Get health status for all targets in a target group.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        
    Returns:
        Dictionary containing target health information
    """
    try:
        response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)
        return response
    except Exception as e:
        print(f"Error getting target health for {target_group_arn}: {str(e)}")
        return {'TargetHealthDescriptions': []}

def analyze_target_health(target_health_descriptions: List[Dict]) -> Dict:
    """
    Analyze target health and categorize by status.
    
    Args:
        target_health_descriptions: List of target health descriptions
        
    Returns:
        Dictionary with health statistics
    """
    stats = {
        'healthy': [],
        'unhealthy': [],
        'initial': [],
        'draining': [],
        'unused': [],
        'unavailable': []
    }
    
    for target in target_health_descriptions:
        state = target['TargetHealth']['State']
        target_id = target['Target']['Id']
        port = target['Target']['Port']
        
        target_info = {
            'id': target_id,
            'port': port,
            'reason': target['TargetHealth'].get('Reason', 'N/A'),
            'description': target['TargetHealth'].get('Description', 'N/A')
        }
        
        if state == 'healthy':
            stats['healthy'].append(target_info)
        elif state == 'unhealthy':
            stats['unhealthy'].append(target_info)
        elif state == 'initial':
            stats['initial'].append(target_info)
        elif state == 'draining':
            stats['draining'].append(target_info)
        elif state == 'unused':
            stats['unused'].append(target_info)
        elif state == 'unavailable':
            stats['unavailable'].append(target_info)
    
    return stats

def generate_health_report(all_health_data: List[Dict]) -> str:
    """
    Generate a formatted health report.
    
    Args:
        all_health_data: List of health data for all target groups
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"ALB Health Check Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    total_unhealthy = 0
    total_healthy = 0
    
    for tg_data in all_health_data:
        tg_name = tg_data['target_group_name']
        tg_arn = tg_data['target_group_arn']
        stats = tg_data['health_stats']
        
        unhealthy_count = len(stats['unhealthy'])
        healthy_count = len(stats['healthy'])
        total_targets = unhealthy_count + healthy_count + len(stats['initial']) + \
                       len(stats['draining']) + len(stats['unused']) + len(stats['unavailable'])
        
        total_unhealthy += unhealthy_count
        total_healthy += healthy_count
        
        report_lines.append(f"Target Group: {tg_name}")
        report_lines.append(f"  ARN: {tg_arn}")
        report_lines.append(f"  Total Targets: {total_targets}")
        report_lines.append(f"  Healthy: {healthy_count}")
        report_lines.append(f"  Unhealthy: {unhealthy_count}")
        
        if stats['unhealthy']:
            report_lines.append("  Unhealthy Targets:")
            for target in stats['unhealthy']:
                report_lines.append(f"    - {target['id']}:{target['port']} - {target['reason']}")
        
        if stats['initial']:
            report_lines.append(f"  Initializing: {len(stats['initial'])}")
        
        if stats['draining']:
            report_lines.append(f"  Draining: {len(stats['draining'])}")
        
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append(f"Summary: {total_healthy} healthy, {total_unhealthy} unhealthy targets")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)

def send_sns_notification(sns_client, topic_arn: str, subject: str, message: str):
    """
    Send notification via SNS if unhealthy targets are detected.
    
    Args:
        sns_client: Boto3 SNS client
        topic_arn: SNS topic ARN
        subject: Notification subject
        message: Notification message
    """
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print(f"Notification sent to {topic_arn}")
    except Exception as e:
        print(f"Error sending SNS notification: {str(e)}")

def export_to_json(all_health_data: List[Dict], filename: str = None):
    """
    Export health data to JSON file.
    
    Args:
        all_health_data: List of health data dictionaries
        filename: Output filename (optional)
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alb_health_report_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(all_health_data, f, indent=2, default=str)
        print(f"Health data exported to {filename}")
    except Exception as e:
        print(f"Error exporting to JSON: {str(e)}")

def main():
    """
    Main execution function.
    """
    # Initialize clients
    elb_client = boto3.client('elbv2', region_name=REGION)
    sns_client = boto3.client('sns', region_name=REGION) if SNS_TOPIC_ARN else None
    
    print("Starting ALB Health Check Monitor...")
    print(f"Region: {REGION}")
    print("")
    
    # Get all target groups
    target_groups = get_all_alb_target_groups(elb_client)
    print(f"Found {len(target_groups)} target groups")
    
    if not target_groups:
        print("No target groups found. Exiting.")
        return
    
    # Collect health data for all target groups
    all_health_data = []
    has_unhealthy = False
    
    for tg in target_groups:
        tg_arn = tg['TargetGroupArn']
        tg_name = tg['TargetGroupName']
        
        print(f"Checking {tg_name}...")
        
        # Get target health
        health_response = get_target_health(elb_client, tg_arn)
        health_descriptions = health_response.get('TargetHealthDescriptions', [])
        
        # Analyze health
        health_stats = analyze_target_health(health_descriptions)
        
        if health_stats['unhealthy']:
            has_unhealthy = True
        
        all_health_data.append({
            'target_group_name': tg_name,
            'target_group_arn': tg_arn,
            'target_group_port': tg.get('Port', 'N/A'),
            'protocol': tg.get('Protocol', 'N/A'),
            'health_check_path': tg.get('HealthCheckPath', 'N/A'),
            'health_stats': health_stats,
            'timestamp': datetime.now().isoformat()
        })
    
    # Generate and print report
    report = generate_health_report(all_health_data)
    print("\n" + report)
    
    # Export to JSON
    export_to_json(all_health_data)
    
    # Send notification if unhealthy targets found
    if has_unhealthy and SNS_TOPIC_ARN and sns_client:
        subject = "ALB Health Check Alert - Unhealthy Targets Detected"
        send_sns_notification(sns_client, SNS_TOPIC_ARN, subject, report)
    
    print("\nHealth check monitoring complete.")

if __name__ == "__main__":
    main()

