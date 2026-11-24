terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# CloudFormation owns the EC2/network foundation. Terraform owns only
# the monitoring layer to avoid creating a duplicate EC2 instance.
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "ems-demo-ec2-cpu-high"
  alarm_description   = "EC2 CPU utilization is above 80 percent for 10 minutes."
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
  dimensions = {
    InstanceId = var.ec2_instance_id
  }
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "ems-demo-memory-high"
  alarm_description   = "CloudWatch Agent memory utilization is above 85 percent."
  namespace           = "CWAgent"
  metric_name         = "mem_used_percent"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = 85
  comparison_operator = "GreaterThanThreshold"
  dimensions = {
    InstanceId = var.ec2_instance_id
  }
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_dashboard" "ems_demo" {
  dashboard_name = "EMS-Demo-Operations"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          title   = "EC2 CPU utilization", view = "timeSeries"
          region  = var.aws_region, period = 300
          metrics = [["AWS/EC2", "CPUUtilization", "InstanceId", var.ec2_instance_id]]
        }
      },
      {
        type = "metric", x = 12, y = 0, width = 12, height = 6
        properties = {
          title   = "EC2 memory utilization", view = "timeSeries"
          region  = var.aws_region, period = 300
          metrics = [["CWAgent", "mem_used_percent", "InstanceId", var.ec2_instance_id]]
        }
      },
      {
        type = "metric", x = 0, y = 6, width = 12, height = 6
        properties = {
          title   = "Root disk utilization", view = "timeSeries"
          region  = var.aws_region, period = 300
          metrics = [["CWAgent", "disk_used_percent", "InstanceId", var.ec2_instance_id, "path", "/", "device", "nvme0n1p1", "fstype", "ext4"]]
        }
      }
    ]
  })
}
