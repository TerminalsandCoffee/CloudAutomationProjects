import boto3
from datetime import datetime

def get_access_advisor_data():
    # Initialize IAM client
    iam = boto3.client('iam')

    # Get access advisor data for IAM roles
    roles = iam.list_roles()['Roles']

    for role in roles:
        role_name = role['RoleName']
        print(f"Analyzing access advisor data for role: {role_name}")

        # Get the access advisor data for the role
        access_advisor_data = iam.get_service_last_accessed_details(
            Arn=role['Arn']
        )

        # Process access advisor data and create a report
        process_access_advisor_data(role_name, access_advisor_data['ServicesLastAccessed'])

    # Get access advisor data for IAM users
    users = iam.list_users()['Users']

    for user in users:
        user_name = user['UserName']
        print(f"Analyzing access advisor data for user: {user_name}")

        # Get the access advisor data for the user
        access_advisor_data = iam.get_service_last_accessed_details(
            Arn=user['Arn']
        )

        # Process access advisor data and create a report
        process_access_advisor_data(user_name, access_advisor_data['ServicesLastAccessed'])

def process_access_advisor_data(entity_name, services_last_accessed):
    if not services_last_accessed:
        print(f"No access advisor data for entity: {entity_name}")
        return

    # Create a report file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_file_name = f"access_advisor_report_{entity_name}_{timestamp}.txt"

    with open(report_file_name, 'w') as report_file:
        report_file.write(f"Access Advisor Report for Entity: {entity_name}\n")
        report_file.write("=" * 50 + "\n\n")

        for service_data in services_last_accessed:
            # Customize the report content based on your needs
            service_name = service_data['ServiceName']
            last_accessed_time = service_data.get('LastAuthenticated', 'N/A')
            
            report_file.write(f"Service: {service_name}\n")
            report_file.write(f"Last Accessed Time: {last_accessed_time}\n")
            report_file.write("=" * 50 + "\n\n")

    print(f"Report generated: {report_file_name}")

if __name__ == "__main__":
    get_access_advisor_data()
