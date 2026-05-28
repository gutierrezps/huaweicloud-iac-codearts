terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.91"
    }
  }
}

variable "vpc_cidr" { default = "10.0.0.0/16" }
variable "subnet_cidr" { default = "10.0.0.0/24" }

provider "huaweicloud" {
  region     = "sa-brazil-1"
  # set environment variables:
  # HW_ACCESS_KEY, HW_SECRET_KEY, HW_SECURITY_TOKEN

  assume_role {
    agency_name = "iac-access-agency"
    # domain_name = HW_ASSUME_ROLE_DOMAIN_NAME environment variable
  }
}

resource "huaweicloud_vpc" "main" {
  name = "vpc-main"
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" "main" {
  name       = "subnet-main"
  cidr       = var.subnet_cidr
  gateway_ip = cidrhost(var.subnet_cidr, 1)
  vpc_id     = huaweicloud_vpc.main.id
}

resource "huaweicloud_vpc_network_acl" "main" {
  name                  = "network-acl-main"
  enabled               = true

  ingress_rules {
    action                 = "allow"
    ip_version             = 4
    protocol               = "icmp"
    source_ip_address      = "10.0.0.0/16"
    destination_ip_address = "0.0.0.0/0"
  }

  associated_subnets {
    subnet_id = huaweicloud_vpc_subnet.main.id
  }
}

data "huaweicloud_account" "current" {}

output "current_account" {
  value = {
    domain_id = data.huaweicloud_account.current.id
    domain_name = data.huaweicloud_account.current.name
  }
}