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
