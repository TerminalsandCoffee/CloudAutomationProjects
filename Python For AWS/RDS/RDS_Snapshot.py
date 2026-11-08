import os
import sys

import boto3

DB_INSTANCE_IDENTIFIER = os.environ["DB_INSTANCE_IDENTIFIER"]
SNAPSHOT_NAME = os.environ["SNAPSHOT_NAME"]
ENCRYPTED_SNAPSHOT_NAME = os.environ["ENCRYPTED_SNAPSHOT_NAME"]
RESTORE_IDENTIFIER = os.environ.get(
    "RESTORE_DB_INSTANCE_IDENTIFIER", f"{DB_INSTANCE_IDENTIFIER}-restored"
)
KMS_KEY_ID = os.environ["KMS_KEY_ID"]
INSTANCE_CLASS = os.environ.get("INSTANCE_CLASS", "db.t3.micro")
EXECUTE = os.environ.get("EXECUTE", "false").lower() == "true"

rds_client = boto3.client("rds")

print(
    f"Plan: snapshot {DB_INSTANCE_IDENTIFIER} -> {SNAPSHOT_NAME}, "
    f"copy encrypted to {ENCRYPTED_SNAPSHOT_NAME}, restore as {RESTORE_IDENTIFIER}"
)
if RESTORE_IDENTIFIER == DB_INSTANCE_IDENTIFIER:
    print("Refusing to restore over the live instance identifier.")
    sys.exit(1)
if not EXECUTE:
    print("Dry run. Set EXECUTE=true to apply.")
    sys.exit(0)

rds_client.create_db_snapshot(
    DBSnapshotIdentifier=SNAPSHOT_NAME,
    DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER,
)
print("Snapshot created:", SNAPSHOT_NAME)

rds_client.copy_db_snapshot(
    SourceDBSnapshotIdentifier=SNAPSHOT_NAME,
    TargetDBSnapshotIdentifier=ENCRYPTED_SNAPSHOT_NAME,
    KmsKeyId=KMS_KEY_ID,
)
print("Encrypted snapshot created:", ENCRYPTED_SNAPSHOT_NAME)

rds_client.restore_db_instance_from_db_snapshot(
    DBInstanceIdentifier=RESTORE_IDENTIFIER,
    DBSnapshotIdentifier=ENCRYPTED_SNAPSHOT_NAME,
    DBInstanceClass=INSTANCE_CLASS,
    MultiAZ=False,
)
print("Restore initiated to", RESTORE_IDENTIFIER)

waiter = rds_client.get_waiter("db_instance_available")
waiter.wait(DBInstanceIdentifier=RESTORE_IDENTIFIER)
print("Restoration completed.")
print("Script execution completed.")
