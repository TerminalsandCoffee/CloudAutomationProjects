policy_name         = "example_policy"
policy_description  = "Example IAM policy created with Terraform"
policy_document     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
EOF

role_name           = "existing_role_name"


# After defining the variables, you can apply the Terraform configuration by running:

# terraform apply -var-file="variables.tfvars"
