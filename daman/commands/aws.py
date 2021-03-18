import argparse

from daman.configure import configure_aws


def configure_aws_command():
    parser = argparse.ArgumentParser(description="Sets up AWS service.")
    parser.add_argument(
        "--access_key_id", type=str, help="AWS access_key_id", required=True,
    )
    parser.add_argument(
        "--secret_access_key", type=str, help="AWS secret_access_key", required=True,
    )
    parser.add_argument(
        "--region", type=str, help="AWS region", required=False,
    )
    args = parser.parse_args()

    configure_aws(
        access_key_id=args.access_key_id,
        secret_access_key=args.secret_access_key,
        region=args.region,
    )
