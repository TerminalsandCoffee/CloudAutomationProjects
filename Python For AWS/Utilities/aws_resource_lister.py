import boto3
import json

def list_event_buses(client):
    print("Listing Event Buses:")
    response = client.list_event_buses()
    buses = response.get('EventBuses', [])
    for bus in buses:
        print(f"- Bus Name: {bus['Name']}, ARN: {bus['Arn']}")
    return [bus['Name'] for bus in buses]

def list_rules_for_bus(client, bus_name):
    print(f"\nListing Rules for Bus: {bus_name}")
    response = client.list_rules(EventBusName=bus_name)
    rules = response.get('Rules', [])
    for rule in rules:
        print(f"- Rule Name: {rule['Name']}, State: {rule['State']}")
    return [rule['Name'] for rule in rules]

def list_targets_for_rule(client, bus_name, rule_name):
    print(f"\nListing Targets for Rule: {rule_name} on Bus: {bus_name}")
    response = client.list_targets_by_rule(EventBusName=bus_name, Rule=rule_name)
    targets = response.get('Targets', [])
    for target in targets:
        print(f"- Target ID: {target['Id']}, ARN: {target['Arn']}")

def list_sns_topics(client):
    print("\nListing SNS Topics:")
    response = client.list_topics()
    topics = response.get('Topics', [])
    for topic in topics:
        print(f"- Topic ARN: {topic['TopicArn']}")
    return [topic['TopicArn'] for topic in topics]

def get_topic_attributes(client, topic_arn):
    print(f"\nGetting Attributes for Topic: {topic_arn}")
    response = client.get_topic_attributes(TopicArn=topic_arn)
    attributes = response.get('Attributes', {})
    print(json.dumps(attributes, indent=2))

def list_subscriptions_for_topic(client, topic_arn):
    print(f"\nListing Subscriptions for Topic: {topic_arn}")
    response = client.list_subscriptions_by_topic(TopicArn=topic_arn)
    subscriptions = response.get('Subscriptions', [])
    for sub in subscriptions:
        print(f"- Subscription ARN: {sub['SubscriptionArn']}, Endpoint: {sub['Endpoint']}")
    return [sub['SubscriptionArn'] for sub in subscriptions if sub['SubscriptionArn'] != 'PendingConfirmation']

def get_subscription_attributes(client, sub_arn):
    print(f"\nGetting Attributes for Subscription: {sub_arn}")
    response = client.get_subscription_attributes(SubscriptionArn=sub_arn)
    attributes = response.get('Attributes', {})
    print(json.dumps(attributes, indent=2))

def main():
    events_client = boto3.client('events')
    sns_client = boto3.client('sns')
    
    # EventBridge section
    bus_names = list_event_buses(events_client)
    for bus in bus_names:
        rule_names = list_rules_for_bus(events_client, bus)
        for rule in rule_names:
            list_targets_for_rule(events_client, bus, rule)
    
    # SNS section
    topic_arns = list_sns_topics(sns_client)
    for topic in topic_arns:
        get_topic_attributes(sns_client, topic)
        sub_arns = list_subscriptions_for_topic(sns_client, topic)
        for sub in sub_arns:
            get_subscription_attributes(sns_client, sub)

if __name__ == "__main__":
    main()
