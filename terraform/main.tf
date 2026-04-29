resource "huaweicloud_vpc" "executor" {
  name = "vpc-executor"
  cidr = "192.168.0.0/16"
}

resource "huaweicloud_vpc_subnet" "executor" {
  name              = "subnet-executor"
  cidr              = "192.168.0.0/24"
  gateway_ip        = "192.168.0.1"
  vpc_id            = huaweicloud_vpc.executor.id
  availability_zone = var.availability_zone
}
