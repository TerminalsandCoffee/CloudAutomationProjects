# Define variables
variable "policy_name" {
  description = "Name of the IAM policy to create"
}

variable "policy_description" {
  description = "Description of the IAM policy to create"
}

variable "policy_document" {
  description = "JSON document defining the IAM policy"
}

variable "role_name" {
  description = "Name of the existing IAM role to attach the policy"
}

# Create IAM policy
resource "aws_iam_policy" "custom_policy" {
  name        = var.policy_name
  description = var.policy_description
  policy      = var.policy_document
}

# Attach IAM policy to existing role
resource "aws_iam_policy_attachment" "attach_policy_to_role" {
  name       = "attach-${var.policy_name}-to-${var.role_name}"
  policy_arn = aws_iam_policy.custom_policy.arn
  roles      = [var.role_name]
}
