import requests
import os
from subprocess import Popen, PIPE, STDOUT
import sys

from apig_sdk import signer

URL_TO_GET_AGENCY_TOKEN = "http://169.254.169.254/openstack/latest/securitykey"


def run_terraform_command(args: list[str]):
    args = ["terraform"] + args
    tf_process = Popen(args, stdout=PIPE, stderr=STDOUT, text=True)
    for line in tf_process.stdout:
        print(line, end="")
    tf_process.wait()
    return_code = tf_process.poll()
    if return_code != 0:
        print(f"Failed to execute terraform command:{args}, return code: {return_code}\n")
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


if __name__ == "__main__":
    # Usage: python Automation.py [action_type]
    # action_type: Optional - Can be 'plan' (default) or 'apply'
    action_type = sys.argv[1] if len(sys.argv) > 1 else "plan"

    ecs_agency_ak, ecs_agency_sk, ecs_agency_token = get_ecs_agency_token()

    os.environ["HW_ACCESS_KEY"] = ecs_agency_ak
    os.environ["HW_SECRET_KEY"] = ecs_agency_sk
    os.environ["HW_SECURITY_TOKEN"] = ecs_agency_token

    run_terraform_command(["init", "-upgrade"])

    if action_type == "apply":
        run_terraform_command(["apply", "-auto-approve"])
    else:
        run_terraform_command(["plan"])
