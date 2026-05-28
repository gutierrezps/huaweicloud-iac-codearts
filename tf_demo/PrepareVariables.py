import os
import shutil
from argparse import ArgumentParser

from Automation import run_terraform_command


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
        "-b", "--bucket_name", default=None,
        help="OBS bucket name to store state file remotely"
    )

    parser.add_argument(
        "-a", "--account_name", required=True,
        help="Huawei Cloud account name to deploy resources"
    )

    args = vars(parser.parse_args())
    bucket_name = args['bucket_name']
    domain_name = args['account_name']

    if os.path.exists(".terraform"):
        shutil.rmtree(".terraform")

    replace_arguments(
        "providers.tf_template",
        DOMAIN_NAME=domain_name)

    if bucket_name is not None:
        replace_arguments(
            "remote_state.tf_template",
            BUCKET_NAME=bucket_name,
            DOMAIN_NAME=domain_name)
    else:
        if os.path.exists("remote_state.tf"):
            os.remove("remote_state.tf")
            run_terraform_command(["init", "-migrate-state"])
