#!/usr/bin/env python3
"""
ALB SSL Certificate Manager

Manages SSL/TLS certificates for Application Load Balancer listeners.
Tracks certificate expiration, supports certificate rotation, and identifies
listeners using certificates that are expiring soon.

Use Cases:
- Certificate expiration monitoring
- Automated certificate rotation
- Security compliance (TLS version enforcement)
- Multi-certificate management
"""

import boto3
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

def get_all_load_balancers(elb_client) -> List[Dict]:
    """
    Get all Application Load Balancers.
    
    Args:
        elb_client: Boto3 ELBv2 client
        
    Returns:
        List of load balancer dictionaries
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

def get_certificate_details(acm_client, certificate_arn: str) -> Optional[Dict]:
    """
    Get details about an ACM certificate.
    
    Args:
        acm_client: Boto3 ACM client
        certificate_arn: ARN of the certificate
        
    Returns:
        Certificate details dictionary or None
    """
    try:
        response = acm_client.describe_certificate(CertificateArn=certificate_arn)
        return response['Certificate']
    except acm_client.exceptions.ResourceNotFoundException:
        print(f"Certificate {certificate_arn} not found in ACM")
        return None
    except Exception as e:
        print(f"Error retrieving certificate: {str(e)}")
        return None

def get_certificate_expiration_date(acm_client, certificate_arn: str) -> Optional[datetime]:
    """
    Get expiration date for a certificate.
    
    Args:
        acm_client: Boto3 ACM client
        certificate_arn: ARN of the certificate
        
    Returns:
        Expiration datetime or None
    """
    cert_details = get_certificate_details(acm_client, certificate_arn)
    if cert_details and 'NotAfter' in cert_details:
        return cert_details['NotAfter'].replace(tzinfo=None)
    return None

def is_certificate_expiring_soon(acm_client, certificate_arn: str, days_threshold: int = 30) -> bool:
    """
    Check if certificate is expiring within the threshold.
    
    Args:
        acm_client: Boto3 ACM client
        certificate_arn: ARN of the certificate
        days_threshold: Number of days to check ahead (default: 30)
        
    Returns:
        True if expiring soon, False otherwise
    """
    expiration = get_certificate_expiration_date(acm_client, certificate_arn)
    if not expiration:
        return False
    
    threshold_date = datetime.now() + timedelta(days=days_threshold)
    return expiration <= threshold_date

def update_listener_certificate(elb_client, listener_arn: str, 
                               old_cert_arn: str, new_cert_arn: str) -> bool:
    """
    Update certificate on a listener.
    
    Args:
        elb_client: Boto3 ELBv2 client
        listener_arn: ARN of the listener
        old_cert_arn: ARN of the certificate to replace
        new_cert_arn: ARN of the new certificate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current listener configuration
        listeners = elb_client.describe_listeners(ListenerArns=[listener_arn])
        if not listeners['Listeners']:
            print(f"Listener {listener_arn} not found")
            return False
        
        listener = listeners['Listeners'][0]
        certificates = listener.get('Certificates', [])
        
        # Update certificates list
        updated_certificates = []
        for cert in certificates:
            if cert['CertificateArn'] == old_cert_arn:
                updated_certificates.append({'CertificateArn': new_cert_arn})
            else:
                updated_certificates.append(cert)
        
        # If old cert not found, add new one
        if not any(c['CertificateArn'] == old_cert_arn for c in certificates):
            updated_certificates.append({'CertificateArn': new_cert_arn})
        
        # Update listener
        elb_client.modify_listener(
            ListenerArn=listener_arn,
            Certificates=updated_certificates
        )
        
        print(f"Successfully updated certificate on listener {listener_arn}")
        return True
    except Exception as e:
        print(f"Error updating listener certificate: {str(e)}")
        return False

def scan_certificates(elb_client, acm_client, region: str, 
                     days_threshold: int = 30) -> List[Dict]:
    """
    Scan all ALBs and their listeners for certificate information.
    
    Args:
        elb_client: Boto3 ELBv2 client
        acm_client: Boto3 ACM client
        region: AWS region
        days_threshold: Days ahead to check for expiration
        
    Returns:
        List of certificate scan results
    """
    results = []
    load_balancers = get_all_load_balancers(elb_client)
    
    print(f"Scanning {len(load_balancers)} Application Load Balancer(s)...")
    
    for lb in load_balancers:
        lb_name = lb['LoadBalancerName']
        lb_arn = lb['LoadBalancerArn']
        
        listeners = get_listeners(elb_client, lb_arn)
        
        for listener in listeners:
            listener_port = listener['Port']
            listener_arn = listener['ListenerArn']
            protocol = listener.get('Protocol', 'HTTP')
            
            # Only check HTTPS listeners
            if protocol != 'HTTPS':
                continue
            
            certificates = listener.get('Certificates', [])
            
            for cert in certificates:
                cert_arn = cert['CertificateArn']
                
                # Get certificate details
                cert_details = get_certificate_details(acm_client, cert_arn)
                expiration = get_certificate_expiration_date(acm_client, cert_arn)
                expiring_soon = is_certificate_expiring_soon(acm_client, cert_arn, days_threshold)
                
                days_until_expiry = None
                if expiration:
                    days_until_expiry = (expiration - datetime.now()).days
                
                result = {
                    'load_balancer_name': lb_name,
                    'load_balancer_arn': lb_arn,
                    'listener_port': listener_port,
                    'listener_arn': listener_arn,
                    'certificate_arn': cert_arn,
                    'domain_name': cert_details.get('DomainName', 'N/A') if cert_details else 'N/A',
                    'expiration_date': expiration.isoformat() if expiration else 'N/A',
                    'days_until_expiry': days_until_expiry,
                    'expiring_soon': expiring_soon,
                    'status': cert_details.get('Status', 'N/A') if cert_details else 'N/A',
                    'in_use': cert_details.get('InUseBy', []) if cert_details else []
                }
                
                results.append(result)
    
    return results

def generate_certificate_report(scan_results: List[Dict]) -> str:
    """
    Generate a formatted certificate report.
    
    Args:
        scan_results: List of certificate scan results
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append(f"ALB SSL Certificate Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 100)
    report_lines.append("")
    
    expiring_count = sum(1 for r in scan_results if r['expiring_soon'])
    expired_count = sum(1 for r in scan_results if r['days_until_expiry'] is not None and r['days_until_expiry'] < 0)
    
    report_lines.append(f"Total Certificates: {len(scan_results)}")
    report_lines.append(f"Expiring Soon (<=30 days): {expiring_count}")
    report_lines.append(f"Expired: {expired_count}")
    report_lines.append("")
    
    # Group by expiration status
    expiring_certs = [r for r in scan_results if r['expiring_soon']]
    if expiring_certs:
        report_lines.append("EXPIRING SOON:")
        report_lines.append("-" * 100)
        for cert in expiring_certs:
            report_lines.append(f"  Load Balancer: {cert['load_balancer_name']}")
            report_lines.append(f"    Listener Port: {cert['listener_port']}")
            report_lines.append(f"    Domain: {cert['domain_name']}")
            report_lines.append(f"    Certificate ARN: {cert['certificate_arn']}")
            report_lines.append(f"    Expires: {cert['expiration_date']} ({cert['days_until_expiry']} days)")
            report_lines.append("")
    
    # All certificates
    report_lines.append("ALL CERTIFICATES:")
    report_lines.append("-" * 100)
    for cert in sorted(scan_results, key=lambda x: x['days_until_expiry'] or 9999):
        status_indicator = "⚠️ " if cert['expiring_soon'] else "✓ "
        report_lines.append(f"{status_indicator} {cert['load_balancer_name']}:{cert['listener_port']} - {cert['domain_name']}")
        report_lines.append(f"    Expires: {cert['expiration_date']} ({cert['days_until_expiry']} days)")
        report_lines.append(f"    ARN: {cert['certificate_arn']}")
        report_lines.append("")
    
    report_lines.append("=" * 100)
    
    return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(
        description='Manage SSL/TLS certificates for Application Load Balancers'
    )
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--days', '-d', type=int, default=30,
                       help='Days threshold for expiration warning (default: 30)')
    parser.add_argument('--scan', action='store_true',
                       help='Scan all ALBs for certificate information')
    parser.add_argument('--update', action='store_true',
                       help='Update certificate on a listener')
    parser.add_argument('--listener-arn', help='Listener ARN (for update)')
    parser.add_argument('--old-cert', help='Old certificate ARN (for update)')
    parser.add_argument('--new-cert', help='New certificate ARN (for update)')
    parser.add_argument('--export-json', help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Initialize clients
    elb_client = boto3.client('elbv2', region_name=args.region)
    acm_client = boto3.client('acm', region_name=args.region)
    
    if args.scan:
        results = scan_certificates(elb_client, acm_client, args.region, args.days)
        report = generate_certificate_report(results)
        print(report)
        
        if args.export_json:
            with open(args.export_json, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults exported to {args.export_json}")
    
    elif args.update:
        if not all([args.listener_arn, args.old_cert, args.new_cert]):
            print("Error: --listener-arn, --old-cert, and --new-cert are required for update")
            return
        
        update_listener_certificate(elb_client, args.listener_arn, args.old_cert, args.new_cert)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

