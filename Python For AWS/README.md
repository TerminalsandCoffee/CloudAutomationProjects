# Python For AWS Automation

A comprehensive collection of Python scripts for automating AWS operations, organized by service for easy navigation and maintenance.

## Organization

This repository is organized by AWS service to improve maintainability and discoverability. Each service folder contains scripts specific to that AWS service.

## Service Directories

### [EC2](./EC2/)
Scripts for managing Amazon Elastic Compute Cloud (EC2) instances, volumes, and snapshots.

**Scripts:**
- `EC2_Snapshot_Inventory.py` - Generate inventory reports of EC2 snapshots
- `EC2NameGenerator.py` - Automated EC2 instance naming utility
- `delete_unattached_volumes.py` / `delete_unattached_volumes_v2.py` - Clean up unattached EBS volumes
- `Increase_Volume_Size.py` - Automate EBS volume resizing
- `replace_volumes.py` - Replace EC2 instance volumes
- `ServerUpgrade.py` - Automated server upgrade workflows
- `SnapShot_Stopped_Instances.py` - Create snapshots of stopped EC2 instances
- `StopEC2v2.py` - Stop EC2 instances programmatically

**Use Cases:**
- Automated instance lifecycle management
- Cost optimization through volume cleanup
- Disaster recovery via snapshot automation
- Infrastructure maintenance workflows

---

### [IAM](./IAM/)
Scripts for managing AWS Identity and Access Management (IAM) users, roles, and permissions.

**Scripts:**
- `Access_Advisor_Report.py` - Generate access advisor reports for IAM entities
- `Access_Analyzer_Report.py` - Analyze IAM access using Access Analyzer
- `AddToGroup_S3Permissions.py` - Add S3 permissions to IAM groups
- `Delete_IAM_Users.py` - Bulk delete IAM users
- `S3_List_IAM_Users.py` - List IAM users with S3 access
- `scan_connect_roles.py` - Scan for AWS Connect service roles and permissions

**Use Cases:**
- Security audits and compliance reporting
- Access review automation
- Permission management at scale
- Least privilege enforcement

---

### [S3](./S3/)
Scripts for managing Amazon Simple Storage Service (S3) buckets and objects.

**Scripts:**
- `S3_Scan.py` - Scan S3 objects for sensitive data (SSN, PII, etc.)

**Use Cases:**
- Security compliance scanning
- Data loss prevention
- Automated security audits

---

### [RDS](./RDS/)
Scripts for managing Amazon Relational Database Service (RDS) instances and configurations.

**Scripts:**
- `RDS_Snapshot.py` - Create and manage RDS snapshots
- `update_rds_sg.py` - Update RDS security group configurations
- `update_rds_sg_inbound_rule.py` - Manage RDS security group inbound rules

**Use Cases:**
- Database backup automation
- Security group management for database access
- Multi-database security group updates
- Disaster recovery preparation

---

### [SQS](./SQS/)
Scripts for managing Amazon Simple Queue Service (SQS) queues and messages.

**Scripts:**
- `SQS.py` - SQS queue management utilities

**Use Cases:**
- Queue monitoring and management
- Message processing automation
- Integration with application workflows

---

### [SNS](./SNS/)
Scripts for managing Amazon Simple Notification Service (SNS) topics and subscriptions.

**Scripts:**
- `EncryptSNSTopic.py` - Encrypt SNS topics for enhanced security

**Use Cases:**
- Security hardening of notification services
- Compliance requirements for encrypted messaging

---

### [ALB](./ALB/)
Scripts for managing Application Load Balancers, including health monitoring, target group management, SSL certificate management, and cost optimization.

**Scripts:**
- `alb_health_check_monitor.py` - Comprehensive health check monitoring across all ALBs and target groups with reporting and alerting
- `alb_target_group_manager.py` - CLI tool for registering/deregistering targets, managing health checks, and connection draining
- `alb_ssl_certificate_manager.py` - Monitor SSL certificate expiration, manage certificate rotation, and track certificate usage
- `alb_cost_optimizer.py` - Identify unused or underutilized ALBs for cost reduction through traffic analysis and usage patterns
- `fetch_lb_logs.py` - Download and process load balancer access logs from S3

**Use Cases:**
- Proactive application health monitoring
- Blue-green and canary deployment automation
- SSL/TLS certificate lifecycle management
- Cost optimization through unused resource identification
- Log analysis and troubleshooting
- Traffic pattern analysis
- Security monitoring

---

### [Lambda](./Lambda/)
AWS Lambda functions and serverless automation scripts.

**Scripts:**
- `SQS_Lambda.py` - Lambda function for processing SQS messages
- `stoppingEC2Lambda.py` - Lambda function to stop EC2 instances (scheduled automation)

**Use Cases:**
- Serverless automation workflows
- Event-driven infrastructure management
- Cost optimization through scheduled actions
- Integration with other AWS services

---

### [Utilities](./Utilities/)
General-purpose utilities and helper scripts that work across multiple AWS services.

**Scripts:**
- `AdvancedNameGenerator.py` - Advanced naming convention generator
- `ComplexNameGenerator.py` - Complex resource naming utilities
- `CreatingListNew.py` - List manipulation utilities (learning/example script)
- `Remove_Tag.py` - Remove tags from AWS resources across services
- `aws_resource_lister.py` - List and enumerate AWS resources across services

**Use Cases:**
- Cross-service automation
- Resource naming standardization
- Tag management at scale
- Resource discovery and inventory

---

## Getting Started

### Prerequisites

- Python 3.7 or higher
- AWS CLI configured with appropriate credentials
- Boto3 library: `pip install boto3`

### AWS Credentials

Scripts use AWS credentials from:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM roles (when running on EC2/Lambda)
4. Some scripts may have hardcoded credentials (⚠️ **Security Warning** - update before production use)

### Installation

```bash
# Install required dependencies
pip install boto3

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install boto3
```

---

## Security Best Practices

**Important Security Notes:**

1. **Never commit credentials** - Remove hardcoded AWS keys before committing
2. **Use IAM roles** - Prefer IAM roles over access keys when possible
3. **Least privilege** - Grant only necessary permissions to IAM users/roles
4. **Rotate credentials** - Regularly rotate access keys
5. **Review scripts** - Always review scripts before execution, especially those that modify or delete resources

### Recommended Approach

```python
# Use environment variables or AWS credentials file
import boto3
import os

# Option 1: Use default credential chain
session = boto3.Session()

# Option 2: Use environment variables
session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

# Option 3: Use IAM role (when running on EC2/Lambda)
# No credentials needed - automatically uses instance/execution role
```

---

## Usage Examples

### EC2 Volume Management

```bash
# List and delete unattached volumes
cd EC2
python delete_unattached_volumes_v2.py
```

### IAM Access Review

```bash
# Generate access advisor report
cd IAM
python Access_Advisor_Report.py
```

### RDS Security Group Update

```bash
# Update RDS security groups
cd RDS
# Edit the script to configure SOURCE_SG_ID, PORT, and RDS_ENDPOINTS
python update_rds_sg.py
```

### Lambda Deployment

```bash
# Package Lambda function
cd Lambda
zip function.zip stoppingEC2Lambda.py
# Deploy via AWS CLI or console
```

### ALB Health Monitoring

```bash
# Monitor all ALB target groups
cd ALB
python alb_health_check_monitor.py

# With SNS notifications
export ALB_HEALTH_SNS_TOPIC_ARN=arn:aws:sns:region:account:topic
python alb_health_check_monitor.py
```

### ALB Target Group Management

```bash
# Register targets
cd ALB
python alb_target_group_manager.py --target-group my-tg register --targets i-1234567890abcdef0:8080,i-0987654321fedcba0:8080

# Deregister with connection draining
python alb_target_group_manager.py --target-group my-tg deregister --targets i-1234567890abcdef0:8080 --drain

# List current targets
python alb_target_group_manager.py --target-group my-tg list
```

### ALB SSL Certificate Management

```bash
# Scan all ALBs for certificate expiration
cd ALB
python alb_ssl_certificate_manager.py --scan --days 30

# Update certificate on a listener
python alb_ssl_certificate_manager.py --update --listener-arn arn:... --old-cert arn:... --new-cert arn:...
```

### ALB Cost Optimization

```bash
# Analyze ALB usage and identify cost savings
cd ALB
python alb_cost_optimizer.py --days 7 --export-json alb_analysis.json
```

---

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines for automated AWS operations:

### GitHub Actions Example

```yaml
name: AWS Automation
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install boto3
      - name: Run cleanup script
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          cd "Python For AWS/EC2"
          python delete_unattached_volumes_v2.py
```

---

## Script Categories

### Cost Optimization
- `EC2/delete_unattached_volumes_v2.py` - Remove unused EBS volumes
- `Lambda/stoppingEC2Lambda.py` - Scheduled instance stopping
- `ALB/alb_cost_optimizer.py` - Identify unused ALBs for cost reduction

### Security & Compliance
- `IAM/Access_Advisor_Report.py` - Access review automation
- `IAM/Access_Analyzer_Report.py` - Security analysis
- `S3/S3_Scan.py` - Sensitive data detection
- `ALB/alb_ssl_certificate_manager.py` - SSL certificate expiration monitoring

### Operations & Maintenance
- `EC2/EC2_Snapshot_Inventory.py` - Snapshot management
- `RDS/RDS_Snapshot.py` - Database backup automation
- `ALB/fetch_lb_logs.py` - Log collection
- `ALB/alb_health_check_monitor.py` - Health monitoring and alerting

### Automation & Orchestration
- `Lambda/*.py` - Serverless automation
- `Utilities/aws_resource_lister.py` - Resource discovery
- `ALB/alb_target_group_manager.py` - Target group automation for deployments

---

## Contributing

When adding new scripts:

1. **Place in appropriate service folder** - If a script spans multiple services, place in `Utilities/`
2. **Follow naming conventions** - Use descriptive, service-prefixed names
3. **Add error handling** - Include try-catch blocks and meaningful error messages
4. **Document usage** - Add comments explaining parameters and use cases
5. **Remove hardcoded credentials** - Use environment variables or parameter passing

---

## Additional Resources

- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Security Best Practices](https://aws.amazon.com/security/security-resources/)

---

## Disclaimer

These scripts are provided as-is for educational and operational purposes. Always test scripts in a non-production environment before deployment. The authors are not responsible for any unintended consequences or costs resulting from the use of these scripts.

**Always review and understand what a script does before executing it, especially scripts that modify or delete AWS resources.**

---

**Organized by service for clarity, efficiency, and maintainability**

