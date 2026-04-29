resource "huaweicloud_codearts_project" "iac" {
  name = "iac"
  type = "scrum"
}

output "codearts_project-iac" {
  value = huaweicloud_codearts_project.iac
}

# TODO: create IAM Agency for ecs-executor
