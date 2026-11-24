# Terraform monitoring layer (alongside CloudFormation)

This project splits IaC ownership:

- **CloudFormation** provisions the demo foundation: EC2, security group, instance role/profile, Elastic IP association and CloudWatch log group.
- **Terraform** provisions only the CloudWatch dashboard and CPU/memory alarms for that existing EC2 instance.

This demonstrates both IaC tools without creating a duplicate EC2 host. Do not use Terraform to recreate CloudFormation-owned resources.

## Prerequisites

- Terraform 1.6+
- AWS CLI authenticated to the same demo account
- Permission to create CloudWatch dashboards and metric alarms
- Existing CloudFormation stack deployed in `ap-southeast-2`
- EC2 instance ID from the stack output

## Commands (PowerShell)

Run from the repository root:

```powershell
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan -var="ec2_instance_id=i-REPLACE_WITH_STACK_INSTANCE_ID"
```

Review the plan. It should create one dashboard and two metric alarms. Then apply:

```powershell
terraform apply -var="ec2_instance_id=i-REPLACE_WITH_STACK_INSTANCE_ID"
```

Terraform state contains infrastructure metadata. Keep `terraform.tfstate*` and `.terraform/` out of Git; never commit credentials or state files.

## Cleanup

Remove only the Terraform-managed monitoring layer:

```powershell
terraform destroy -var="ec2_instance_id=i-REPLACE_WITH_STACK_INSTANCE_ID"
```

This does not delete the CloudFormation stack or EC2 instance. Delete the CloudFormation stack separately only after confirming you no longer need the host, Elastic IP, log group, or stored data.

## Design notes

- CloudFormation remains the source of truth for the EC2 foundation.
- Terraform references the instance by ID; it does not import or manage it.
- Missing metric data is treated as non-breaching, avoiding false high-utilization alarms while the demo instance is stopped.
- Notifications are not configured because no SNS destination has been supplied.
