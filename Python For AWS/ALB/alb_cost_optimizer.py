#!/usr/bin/env python3
"""
ALB Cost Optimizer

Identifies unused or underutilized Application Load Balancers for cost optimization.
Analyzes ALB usage patterns, target group health, and traffic patterns to recommend
candidates for deletion or consolidation.

Use Cases:
- Cost reduction through unused resource identification
- Infrastructure cleanup
- Right-sizing recommendations
- Multi-ALB consolidation opportunities
"""

import boto3
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

def get_all_load_balancers(elb_client) -> List[Dict]:
    """
    Get all Application Load Balancers with detailed information.
    
    Args:
        elb_client: Boto3 ELBv2 client
        
    Returns:
        List of load balancer dictionaries with additional metadata
    """
    load_balancers = []
    paginator = elb_client.get_paginator('describe_load_balancers')
    
    try:
        for page in paginator.paginate():
            for lb in page['LoadBalancers']:
                if lb['Type'] == 'application':  # Only ALBs
                    load_balancers.append(lb)
    except Exception as e:
        print(f"Error retrieving load balancers: {str(e)}")
        raise
    
    return load_balancers

def get_listeners(elb_client, load_balancer_arn: str) -> List[Dict]:
    """
    Get all listeners for a load balancer.
    
    Args:
        elb_client: Boto3 ELBv2 client
        load_balancer_arn: ARN of the load balancer
        
    Returns:
        List of listener dictionaries
    """
    try:
        response = elb_client.describe_listeners(LoadBalancerArn=load_balancer_arn)
        return response.get('Listeners', [])
    except Exception as e:
        print(f"Error retrieving listeners: {str(e)}")
        return []

def get_target_groups_for_alb(elb_client, load_balancer_arn: str) -> List[Dict]:
    """
    Get all target groups associated with a load balancer.
    
    Args:
        elb_client: Boto3 ELBv2 client
        load_balancer_arn: ARN of the load balancer
        
    Returns:
        List of target group dictionaries
    """
    try:
        response = elb_client.describe_target_groups(LoadBalancerArn=load_balancer_arn)
        return response.get('TargetGroups', [])
    except Exception as e:
        print(f"Error retrieving target groups: {str(e)}")
        return []

def get_target_health_summary(elb_client, target_group_arn: str) -> Dict:
    """
    Get summary of target health for a target group.
    
    Args:
        elb_client: Boto3 ELBv2 client
        target_group_arn: ARN of the target group
        
    Returns:
        Dictionary with health summary statistics
    """
    try:
        response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)
        targets = response.get('TargetHealthDescriptions', [])
        
        healthy = sum(1 for t in targets if t['TargetHealth']['State'] == 'healthy')
        unhealthy = sum(1 for t in targets if t['TargetHealth']['State'] == 'unhealthy')
        total = len(targets)
        
        return {
            'total': total,
            'healthy': healthy,
            'unhealthy': unhealthy,
            'has_targets': total > 0,
            'all_healthy': healthy > 0 and unhealthy == 0
        }
    except Exception as e:
        print(f"Error getting target health: {str(e)}")
        return {'total': 0, 'healthy': 0, 'unhealthy': 0, 'has_targets': False, 'all_healthy': False}

def get_cloudwatch_metrics(cloudwatch_client, load_balancer_name: str, 
                          days: int = 7) -> Dict:
    """
    Get CloudWatch metrics for load balancer to assess usage.
    
    Args:
        cloudwatch_client: Boto3 CloudWatch client
        load_balancer_name: Name of the load balancer
        days: Number of days to look back
        
    Returns:
        Dictionary with metric statistics
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    metrics = {}
    
    # Request count metric
    try:
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='RequestCount',
            Dimensions=[
                {'Name': 'LoadBalancer', 'Value': load_balancer_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily
            Statistics=['Sum']
        )
        
        total_requests = sum(point['Sum'] for point in response['Datapoints'])
        metrics['total_requests'] = total_requests
        metrics['avg_daily_requests'] = total_requests / days if days > 0 else 0
        metrics['has_traffic'] = total_requests > 0
    except Exception as e:
        print(f"Error getting request count metric: {str(e)}")
        metrics['total_requests'] = 0
        metrics['avg_daily_requests'] = 0
        metrics['has_traffic'] = False
    
    # Active connection count
    try:
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='ActiveConnectionCount',
            Dimensions=[
                {'Name': 'LoadBalancer', 'Value': load_balancer_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # Hourly
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            avg_connections = sum(point['Average'] for point in response['Datapoints']) / len(response['Datapoints'])
            metrics['avg_connections'] = avg_connections
        else:
            metrics['avg_connections'] = 0
    except Exception as e:
        metrics['avg_connections'] = 0
    
    return metrics

def analyze_alb_usage(elb_client, cloudwatch_client, load_balancer: Dict, 
                     days: int = 7) -> Dict:
    """
    Analyze ALB usage and determine if it's a candidate for deletion.
    
    Args:
        elb_client: Boto3 ELBv2 client
        cloudwatch_client: Boto3 CloudWatch client
        load_balancer: Load balancer dictionary
        days: Days to analyze for usage
        
    Returns:
        Dictionary with analysis results
    """
    lb_arn = load_balancer['LoadBalancerArn']
    lb_name = load_balancer['LoadBalancerName']
    
    # Get listeners
    listeners = get_listeners(elb_client, lb_arn)
    has_listeners = len(listeners) > 0
    
    # Get target groups
    target_groups = get_target_groups_for_alb(elb_client, lb_arn)
    has_target_groups = len(target_groups) > 0
    
    # Analyze target health
    total_targets = 0
    healthy_targets = 0
    has_healthy_targets = False
    
    for tg in target_groups:
        health = get_target_health_summary(elb_client, tg['TargetGroupArn'])
        total_targets += health['total']
        healthy_targets += health['healthy']
        if health['healthy'] > 0:
            has_healthy_targets = True
    
    # Get CloudWatch metrics
    metrics = get_cloudwatch_metrics(cloudwatch_client, lb_name, days)
    
    # Determine if candidate for deletion
    deletion_candidate = False
    deletion_reasons = []
    
    if not has_listeners:
        deletion_candidate = True
        deletion_reasons.append("No listeners configured")
    
    if not has_target_groups:
        deletion_candidate = True
        deletion_reasons.append("No target groups attached")
    
    if not has_healthy_targets and total_targets > 0:
        deletion_candidate = True
        deletion_reasons.append("No healthy targets")
    
    if not metrics.get('has_traffic', False):
        deletion_candidate = True
        deletion_reasons.append(f"No traffic in last {days} days")
    
    # Calculate estimated monthly cost (ALB base cost ~$16/month + LCU costs)
    estimated_monthly_cost = 16.20  # Base ALB cost
    if metrics.get('total_requests', 0) > 0:
        # Rough estimate: assume some LCU usage
        estimated_monthly_cost += 5.0
    
    analysis = {
        'load_balancer_name': lb_name,
        'load_balancer_arn': lb_arn,
        'scheme': load_balancer.get('Scheme', 'N/A'),
        'state': load_balancer.get('State', {}).get('Code', 'N/A'),
        'created_time': load_balancer.get('CreatedTime', 'N/A'),
        'listeners_count': len(listeners),
        'target_groups_count': len(target_groups),
        'total_targets': total_targets,
        'healthy_targets': healthy_targets,
        'has_listeners': has_listeners,
        'has_target_groups': has_target_groups,
        'has_healthy_targets': has_healthy_targets,
        'metrics': metrics,
        'deletion_candidate': deletion_candidate,
        'deletion_reasons': deletion_reasons,
        'estimated_monthly_cost': round(estimated_monthly_cost, 2),
        'tags': load_balancer.get('Tags', [])
    }
    
    return analysis

def generate_optimization_report(analyses: List[Dict]) -> str:
    """
    Generate a formatted cost optimization report.
    
    Args:
        analyses: List of ALB analysis dictionaries
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append(f"ALB Cost Optimization Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 100)
    report_lines.append("")
    
    candidates = [a for a in analyses if a['deletion_candidate']]
    total_monthly_cost = sum(a['estimated_monthly_cost'] for a in analyses)
    potential_savings = sum(a['estimated_monthly_cost'] for a in candidates)
    
    report_lines.append(f"Total ALBs Analyzed: {len(analyses)}")
    report_lines.append(f"Deletion Candidates: {len(candidates)}")
    report_lines.append(f"Total Estimated Monthly Cost: ${total_monthly_cost:.2f}")
    report_lines.append(f"Potential Monthly Savings: ${potential_savings:.2f}")
    report_lines.append(f"Potential Annual Savings: ${potential_savings * 12:.2f}")
    report_lines.append("")
    
    if candidates:
        report_lines.append("DELETION CANDIDATES:")
        report_lines.append("-" * 100)
        for candidate in candidates:
            report_lines.append(f"  Load Balancer: {candidate['load_balancer_name']}")
            report_lines.append(f"    ARN: {candidate['load_balancer_arn']}")
            report_lines.append(f"    Estimated Monthly Cost: ${candidate['estimated_monthly_cost']:.2f}")
            report_lines.append(f"    Reasons:")
            for reason in candidate['deletion_reasons']:
                report_lines.append(f"      - {reason}")
            report_lines.append(f"    Listeners: {candidate['listeners_count']}")
            report_lines.append(f"    Target Groups: {candidate['target_groups_count']}")
            report_lines.append(f"    Total Targets: {candidate['total_targets']} ({candidate['healthy_targets']} healthy)")
            report_lines.append(f"    Traffic (7 days): {candidate['metrics'].get('total_requests', 0):,} requests")
            report_lines.append("")
    
    report_lines.append("ALL LOAD BALANCERS:")
    report_lines.append("-" * 100)
    for analysis in sorted(analyses, key=lambda x: x['estimated_monthly_cost'], reverse=True):
        status = "CANDIDATE FOR DELETION" if analysis['deletion_candidate'] else "ACTIVE"
        report_lines.append(f"  {status}: {analysis['load_balancer_name']}")
        report_lines.append(f"    Cost: ${analysis['estimated_monthly_cost']:.2f}/month")
        report_lines.append(f"    Traffic: {analysis['metrics'].get('total_requests', 0):,} requests (7 days)")
        report_lines.append(f"    Targets: {analysis['healthy_targets']}/{analysis['total_targets']} healthy")
        report_lines.append("")
    
    report_lines.append("=" * 100)
    
    return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(
        description='Identify unused or underutilized ALBs for cost optimization'
    )
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Days to analyze for traffic (default: 7)')
    parser.add_argument('--export-json', help='Export results to JSON file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show analysis without taking action')
    
    args = parser.parse_args()
    
    # Initialize clients
    elb_client = boto3.client('elbv2', region_name=args.region)
    cloudwatch_client = boto3.client('cloudwatch', region_name=args.region)
    
    print("Analyzing Application Load Balancers...")
    print(f"Region: {args.region}")
    print(f"Analysis period: {args.days} days")
    print("")
    
    # Get all ALBs
    load_balancers = get_all_load_balancers(elb_client)
    print(f"Found {len(load_balancers)} Application Load Balancer(s)")
    print("")
    
    # Analyze each ALB
    analyses = []
    for lb in load_balancers:
        print(f"Analyzing {lb['LoadBalancerName']}...")
        analysis = analyze_alb_usage(elb_client, cloudwatch_client, lb, args.days)
        analyses.append(analysis)
    
    # Generate report
    report = generate_optimization_report(analyses)
    print(report)
    
    # Export to JSON if requested
    if args.export_json:
        with open(args.export_json, 'w') as f:
            json.dump(analyses, f, indent=2, default=str)
        print(f"\nAnalysis exported to {args.export_json}")
    
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()

