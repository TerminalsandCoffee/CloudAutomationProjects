#!/bin/bash

# Path to the text file containing AMI IDs (one per line)
AMI_FILE_PATH=/home/yaboy/customers/<clientname>/ami_list.txt

#replace path with the correct one. 

# Read AMI IDs from the text file and delete each AMI
cat $AMI_FILE_PATH | while read ami_id; do
    echo "Deleting AMI: $ami_id"

        # Deregister the AMI
            aws ec2 deregister-image --image-id $ami_id --profile ACCTNUMBER --region REGION

                # Find associated snapshots and delete them
                    snapshot_ids=$(aws ec2 describe-images --image-ids $ami_id --query 'Images[].BlockDeviceMappings[].Ebs.SnapshotId' --profile ACCTNUMBER --region REGION --output text)
                        for snapshot_id in $snapshot_ids; do
                                        echo "Deleting Snapshot: $snapshot_id"
                                                aws ec2 delete-snapshot --snapshot-id $snapshot_id --profile ACCTNUMBER --region REGION
                                                    done

                                                        echo "AMI $ami_id and its associated snapshots deleted"
                                                done
