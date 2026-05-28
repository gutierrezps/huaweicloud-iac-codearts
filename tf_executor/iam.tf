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
        },
        {
          "Effect": "Allow",
          "Action": [
            "iam:tokens:assume"
          ],
          "Resource": [
            "iam::*:agencies:iac-intermediate-agency",
            "iam::*:agencies:iac-access-agency",
          ]
        },
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
    })
}

resource "huaweicloud_identity_agency" "executor" {
  name                  = "iac-executor-agency"
  delegated_domain_name = "op_svc_ecs"

  all_resources_roles = [
    "VPC FullAccess"  # used only to provision tf_demo in current account
  ]

  # As of 2026-05-21, Terraform provider v1.91.0 does not have a way
  # to attach an Identity Policy to an Agency.

  # Go to new IAM console and manually attach the "iac-executor-policy-v5"
  # identity policy to this agency

  lifecycle {
    ignore_changes = [
      # Issue on v1.91.0, where this legacy argument is always updated to
      # "null" when delegating access to a cloud service like ECS (op_svc_ecs)
      delegated_service_name
    ]
  }
}

resource "huaweicloud_identity_agency" "intermediate" {
  name                  = "iac-intermediate-agency"
  delegated_domain_name = data.huaweicloud_account.current.name

  # As of 2026-05-21, Terraform provider v1.91.0 does not have a way
  # to attach an Identity Policy to an Agency.

  # Go to new IAM console and manually attach the "iac-executor-policy-v5"
  # identity policy to this agency

  # This agency is not required to operate other accounts. Its purpose is to
  # demonstrate a complex scenario where the target account cannot be operated
  # directly by the Terraform executor account
}