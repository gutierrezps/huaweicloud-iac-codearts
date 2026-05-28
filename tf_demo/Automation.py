import requests
import os
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser

import shutil

URL_TO_GET_AGENCY_TOKEN = "http://169.254.169.254/openstack/latest/securitykey"


def run_terraform_command(args: list[str]):
    args = ["terraform"] + args
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


def replace_arguments(filename: str, **kwargs):
    contents = ""

    with open(filename) as f:
        contents = f.read()

    for placeholder, value in kwargs.items():
        contents = contents.replace(f"{placeholder}_PLACEHOLDER", value)

    output_filename = filename.replace("_template", "")
    with open(output_filename, 'w') as f:
        f.write(contents)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "action_type",
        choices=["plan", "apply", "plan_destroy", "destroy"]
        )

    parser.add_argument(
        "-b", "--bucket_name", default=None,
        help="OBS bucket name to store state file remotely"
    )

    parser.add_argument(
        "-a", "--account_name", default=None,
        help="Huawei Cloud account name to deploy resources"
    )

    args = vars(parser.parse_args())
    action_type = args['action_type']
    bucket_name = args['bucket_name']
    domain_name = args['account_name']

    ecs_agency_ak, ecs_agency_sk, ecs_agency_token = get_ecs_agency_token()

    os.environ["HW_ACCESS_KEY"] = ecs_agency_ak
    os.environ["HW_SECRET_KEY"] = ecs_agency_sk
    os.environ["HW_SECURITY_TOKEN"] = ecs_agency_token

    # used by remote state
    os.environ["AWS_ACCESS_KEY_ID"] = ecs_agency_ak
    os.environ["AWS_SECRET_ACCESS_KEY"] = ecs_agency_sk
    os.environ["AWS_SESSION_TOKEN"] = ecs_agency_token
    os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"
    os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"

    os.environ["HW_ASSUME_ROLE_DOMAIN_NAME"] = domain_name

    if os.path.exists(".terraform"):
        shutil.rmtree(".terraform")

    if bucket_name is not None:
        replace_arguments(
            "remote_state.tf_template",
            BUCKET_NAME=bucket_name,
            DOMAIN_NAME=domain_name)
    else:
        if os.path.exists("remote_state.tf"):
            os.remove("remote_state.tf")
            run_terraform_command(["init", "-migrate-state"])

    run_terraform_command(["init", "-upgrade"])

    if action_type == "apply":
        run_terraform_command(["apply", "-auto-approve"])
    elif action_type == "plan_destroy":
        run_terraform_command(["plan", "-destroy"])
    elif action_type == "destroy":
        run_terraform_command(["destroy", "-auto-approve"])
    else:
        run_terraform_command(["plan"])
