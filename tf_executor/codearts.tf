resource "huaweicloud_codearts_project" "iac" {
  name = "iac"
  type = "scrum"
}

resource "huaweicloud_identityv5_policy" "executor" {
  name            = "iac-executor-policy-v5"
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

resource "huaweicloud_identity_role" "executor" {
  name        = "iac-executor-policy-v3"
  description = "iac-executor-policy-v3"
  type        = "AX"
  policy      = <<EOT
{
  "Version": "1.1",
  "Statement": [
    {
      "Action": [
        "obs:bucket:HeadBucket",
        "obs:bucket:ListBucket",
        "obs:bucket:GetBucketLocation",
        "obs:object:GetObject",
        "obs:object:GetObjectVersion",
        "obs:object:PutObject",
        "obs:object:DeleteObject"
      ],
      "Effect": "Allow",
      "Resource": [
        "obs:::bucket:${var.obs_bucket_name}",
        "obs:::object:${var.obs_bucket_name}/*"
      ]
    }
  ]
}
EOT
}

resource "huaweicloud_identity_agency" "executor" {
  name                  = "iac-executor-agency"
  delegated_domain_name = "op_svc_ecs"

  all_resources_roles = [
    "iac-executor-policy-v3",
    "VPC FullAccess"  # used only to provision tf_demo in current account
    ]

  # As of 2026-05-21, Terraform provider v1.91.0 does not have a way
  # to attach an Identity Policy to an Agency.

  # Go to new IAM console and manually attach the "iac-executor-policy-v5"
  # identity policy to this agency
}