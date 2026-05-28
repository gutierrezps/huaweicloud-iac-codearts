import json
import os
from argparse import ArgumentParser
from subprocess import PIPE, STDOUT, Popen

import requests
from apig_sdk import signer

URL_TO_GET_AGENCY_TOKEN = "http://169.254.169.254/openstack/latest/securitykey"

# URN of intermediate agency, used to obtain the temporary credentials of
# accounts to deploy resources. The format is the following:
# iam::{DOMAIN_ID}:agency:{AGENCY_NAME}
INTERMEDIATE_AGENCY_URN = "iam::28e76e9689f340649e1cbbfc927128d3:agency:iac-intermediate-agency"  # noqa:E501


def run_terraform_command(args: list[str]):
    args = ["terraform"] + args + ["-no-color"]
    tf_process = Popen(args, stdout=PIPE, stderr=STDOUT, text=True)
    for line in tf_process.stdout:
        print(line, end="")
    tf_process.wait()
    return_code = tf_process.poll()
    if return_code != 0:
        msg = f"Failed to execute terraform command: {args}"
        msg += f", return code: {return_code}\n"
        print(msg)
        exit(1)


def get_ecs_agency_token():
    ecs_agency_ak, ecs_agency_sk, ecs_agency_token = None, None, None
    headers = {}

    resp = requests.get(URL_TO_GET_AGENCY_TOKEN, headers=headers, timeout=3)
    data = resp.json()
    if data.get('credential'):
        ecs_agency_ak = data['credential']['access']
        ecs_agency_sk = data['credential']['secret']
        ecs_agency_token = data['credential']['securitytoken']
    else:
        raise Exception("Failed to get the temporary credential of ECS agency")

    return ecs_agency_ak, ecs_agency_sk, ecs_agency_token


def get_intermediate_agency_token(
        temp_ak: str, temp_sk: str, temp_token: str,
        agency_urn: str, region: str) -> tuple[str, str, str]:
    """Use temporary credentials to get the other temporary AK, SK and
    security token of other agency specified by agency_urn

    Args:
        temp_ak (str): Temporary AK
        temp_sk (str): Temporary SK
        temp_token (str): Temporary security token
        agency_urn (str): URN of intermediate agency used to obtain final AK/SK
        region (str): region code, e.g. 'sa-brazil-1'

    Returns:
        tuple[str, str, str]: Intermediate agency AK, SK and Security Token
    """
    agency_ak, agency_sk, agency_token = None, None, None
    if temp_ak is None or temp_sk is None or temp_token is None:
        return None

    sig = signer.Signer()
    sig.Key = temp_ak
    sig.Secret = temp_sk

    url = f"https://sts.{region}.myhuaweicloud.com/v5/agencies/assume"
    req = signer.HttpRequest("POST", url)
    req.headers = {
        "Content-Type": "application/json",
        "X-Security-Token": temp_token
        }
    payload = {
        "duration_seconds": 3600,
        "agency_urn": agency_urn,
        "agency_session_name": "automation_agency_session"
    }
    req.body = json.dumps(payload)

    sig.Sign(req)
    resp = requests.post(url, headers=req.headers, data=req.body)
    agency_credentials = resp.json()

    if "credentials" in agency_credentials:
        agency_ak = agency_credentials["credentials"]["access_key_id"]
        agency_sk = agency_credentials["credentials"]["secret_access_key"]
        agency_token = agency_credentials["credentials"]["security_token"]
    else:
        print(agency_credentials)
        msg = "Failed to get temporary credentials of intermediate agency"
        raise Exception(msg)

    return agency_ak, agency_sk, agency_token


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "action_type",
        choices=["plan", "apply", "plan_destroy", "destroy"]
        )

    args = vars(parser.parse_args())
    action_type = args['action_type']

    ecs_agency_ak, ecs_agency_sk, ecs_agency_token = get_ecs_agency_token()

    tf_ak, tf_sk, tf_token = ecs_agency_ak, ecs_agency_sk, ecs_agency_token

    # Intermediate agency demo. Remove/comment the following lines
    # to use the same ECS agency to run the Terraform code
    tf_ak, tf_sk, tf_token = get_intermediate_agency_token(
        ecs_agency_ak, ecs_agency_sk, ecs_agency_token,
        INTERMEDIATE_AGENCY_URN, "sa-brazil-1")

    os.environ["HW_ACCESS_KEY"] = tf_ak
    os.environ["HW_SECRET_KEY"] = tf_sk
    os.environ["HW_SECURITY_TOKEN"] = tf_token

    # used by remote state
    os.environ["AWS_ACCESS_KEY_ID"] = ecs_agency_ak
    os.environ["AWS_SECRET_ACCESS_KEY"] = ecs_agency_sk
    os.environ["AWS_SESSION_TOKEN"] = ecs_agency_token
    os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"
    os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"

    run_terraform_command(["init", "-upgrade"])

    if action_type == "apply":
        run_terraform_command(["apply", "-auto-approve"])
    elif action_type == "plan_destroy":
        run_terraform_command(["plan", "-destroy"])
    elif action_type == "destroy":
        run_terraform_command(["destroy", "-auto-approve"])
    else:
        run_terraform_command(["plan"])
