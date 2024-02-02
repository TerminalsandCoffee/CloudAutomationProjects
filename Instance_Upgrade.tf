provider "aws" {
  region = "your_aws_region"
}

resource "aws_instance" "example_instance" {
  ami           = "your_ami_id"
  instance_type = "your_instance_type"
}

resource "aws_instance" "example_instance_snapshot" {
  count         = length(aws_instance.example_instance)
  ami           = aws_instance.example_instance[count.index].ami
  instance_type = aws_instance.example_instance[count.index].instance_type

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_volume_attachment" "example_attachment" {
  count          = length(aws_instance.example_instance)
  instance_id    = aws_instance.example_instance[count.index].id
  volume_id      = aws_instance.example_instance[count.index].root_block_device[0].volume_id
}

resource "aws_snapshot" "example_snapshot" {
  count        = length(aws_instance.example_instance_snapshot)
  volume_id    = aws_volume_attachment.example_attachment[count.index].volume_id
  description  = "Snapshot for instance ${aws_instance.example_instance_snapshot[count.index].id}"
}

# Use the aws_instance resource to start and stop the instance.
# Note: Modifying the instance type using Terraform is not a common use case, 
# and it's generally recommended to create a new instance with the desired type.

# Use "terraform apply" to apply the changes.



# Adds CloudWatch Events rule to trigger the Terraform script every Saturday at 9 AM (EST)

/*

resource "aws_cloudwatch_event_rule" "schedule" {
  name        = "terraform-schedule-rule"
  description = "Run Terraform every Saturday at 9 AM EST"
  schedule_expression = "cron(0 9 ? * SAT *)"  # Schedule for 9 AM on Saturdays
}

resource "aws_cloudwatch_event_target" "target" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  arn       = "your_lambda_function_arn"  # Replace with your Lambda function or SSM document ARN that executes Terraform
}

# Grant necessary permissions to CloudWatch Events to trigger Lambda function or SSM document
resource "aws_lambda_permission" "permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "your_lambda_function_name"
  principal     = "events.amazonaws.com"

  source_arn = aws_cloudwatch_event_rule.schedule.arn
}

*/

