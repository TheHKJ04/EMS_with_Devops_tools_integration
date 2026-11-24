variable "aws_region" {
  description = "AWS region containing the CloudFormation EMS demo stack."
  type        = string
  default     = "ap-southeast-2"
}

variable "ec2_instance_id" {
  description = "EC2 instance ID created by the CloudFormation stack."
  type        = string
}
