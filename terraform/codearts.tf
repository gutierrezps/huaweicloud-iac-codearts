resource "huaweicloud_codearts_project" "iac" {
  name = "iac"
  type = "scrum"
}

resource "huaweicloud_identityv5_policy" "executor" {
  name            = "iac-executor-policy"
  policy_document = jsonencode(
    {
      "Version": "5.0",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "sts::setSourceIdentity",
            "sts::tagSession",
            "sts:agencies:assume"
          ]
        }
      ]
    })
}

resource "huaweicloud_identity_agency" "executor" {
  name                  = "iac-executor-agency"
  delegated_domain_name = "op_svc_ecs"
  domain_roles          = ["iac-executor-policy"]
}