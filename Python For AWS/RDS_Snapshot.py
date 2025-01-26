import boto3
import time

# Replace these variables with your actual values
DB_INSTANCE_IDENTIFIER = "rafs-test-db"
SNAPSHOT_NAME = "rafs-test-db-snapshot"
ENCRYPTED_SNAPSHOT_NAME = "rafs-test-db-encrypted-snapshot"
#KMS_KEY_ID = "arn:aws:kms:"
INSTANCE_CLASS = "db.t2.micro"

# Create an RDS client
rds_client = boto3.client('rds')

# Create Snapshot
response = rds_client.create_db_snapshot(
    DBSnapshotIdentifier=SNAPSHOT_NAME,
    DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER
)
print("Snapshot created:", SNAPSHOT_NAME)

#  Copy the Snapshot to a New Snapshot with KMS Encryption
response = rds_client.copy_db_snapshot(
    SourceDBSnapshotIdentifier=SNAPSHOT_NAME,
    TargetDBSnapshotIdentifier=ENCRYPTED_SNAPSHOT_NAME,
#    KmsKeyId=KMS_KEY_ID
)
print("Encrypted snapshot created:", ENCRYPTED_SNAPSHOT_NAME)

# In-Place Restore using the Encrypted Snapshot
response = rds_client.restore_db_instance_from_db_snapshot(
    DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER,
    DBSnapshotIdentifier=ENCRYPTED_SNAPSHOT_NAME,
    DBInstanceClass=INSTANCE_CLASS,
    MultiAZ=False
)
print("In-Place restore initiated.")

# Verify the In-Place Restore
print("Waiting for the restoration to complete...")
waiter = rds_client.get_waiter('db_instance_available')
waiter.wait(DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER)
print("Restoration completed.")

# print when completed 
print("Script execution completed.")
