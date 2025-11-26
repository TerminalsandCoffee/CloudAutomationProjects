"""
This is a python script that pulls data from the
AWS Identity and Access Management Access Analyzer
and creates a report of the findings
"""
import boto3
from datetime import datetime

def analyze_access_analyzer():
    # Initialize IAM Access Analyzer client
    access_analyzer = boto3.client('accessanalyzer')

    # List analyzers
    analyzers = access_analyzer.list_analyzers()

    # Iterate through analyzers and get findings
    for analyzer in analyzers['analyzers']:
        analyzer_name = analyzer['name']
        print(f"Analyzing findings for analyzer: {analyzer_name}")

        # Get findings for the analyzer
        findings = access_analyzer.list_findings(analyzerArn=analyzer['arn'])

        # Process findings and create a report
        process_findings(analyzer_name, findings['findings'])

def process_findings(analyzer_name, findings):
    if not findings:
        print(f"No findings for analyzer: {analyzer_name}")
        return

    # Create a report file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_file_name = f"access_analyzer_report_{analyzer_name}_{timestamp}.txt"

    with open(report_file_name, 'w') as report_file:
        report_file.write(f"Access Analyzer Report for {analyzer_name}\n")
        report_file.write("=" * 50 + "\n\n")

        for finding in findings:
            # Customize the report content based on your needs
            report_file.write(f"Finding ID: {finding['id']}\n")
            report_file.write(f"Resource: {finding['resourceArn']}\n")
            report_file.write(f"Type: {finding['findingType']}\n")
            report_file.write(f"Details: {finding['details']}\n")
            report_file.write("=" * 50 + "\n\n")

    print(f"Report generated: {report_file_name}")

if __name__ == "__main__":
    analyze_access_analyzer()
