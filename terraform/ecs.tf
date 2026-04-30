data "http" "ingress_ip_address" {
  # Returns public IP address of this machine,
  # that is executing this Terraform code.
  # SSH to the ecs-executor machine will only be allowed from this machine.

  url = "https://api.ipify.org/"
}

locals {
  ingress_ip_address = trimspace(data.http.ingress_ip_address.response_body)
}

resource "huaweicloud_networking_secgroup" "executor" {
  name                 = "sg-executor"
  description          = "SG for ecs-executor of CodeArts pipeline"
  delete_default_rules = true
}

resource "huaweicloud_networking_secgroup_rule" "executor_egr" {
  security_group_id = huaweicloud_networking_secgroup.executor.id
  direction         = "egress"
  ethertype         = "IPv4"
}

resource "huaweicloud_networking_secgroup_rule" "executor_egr_v4" {
  security_group_id = huaweicloud_networking_secgroup.executor.id
  direction         = "egress"
  ethertype         = "IPv6"
}

resource "huaweicloud_networking_secgroup_rule" "executor_ing_ssh" {
  security_group_id = huaweicloud_networking_secgroup.executor.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  ports    = "22"
  remote_ip_prefix  = "${local.ingress_ip_address}/32"
}

data "huaweicloud_compute_flavors" "executor" {
  availability_zone = var.availability_zone
  performance_type  = "normal"
  cpu_core_count    = 2
  memory_size       = 4
}

resource "huaweicloud_vpc_eip" "executor" {
  name = "eip-executor"

  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "bandwidth-eip-executor"
    size        = 300
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

resource "huaweicloud_compute_instance" "executor" {
  name               = "ecs-executor"
  image_name         = "Ubuntu 22.04 server 64bit"
  flavor_id          = data.huaweicloud_compute_flavors.executor.ids[0]
  admin_pass         = var.default_password
  security_group_ids = [huaweicloud_networking_secgroup.executor.id]
  availability_zone  = var.availability_zone
  agency_name        = huaweicloud_identity_agency.executor.name

  system_disk_type = "SAS"
  system_disk_size = 40

  eip_id = huaweicloud_vpc_eip.executor.id

  agent_list = "ces"

  network {
    uuid = huaweicloud_vpc_subnet.executor.id
  }
}
