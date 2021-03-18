import argparse
from daman import daman as dm


def delete_command():
    parser = argparse.ArgumentParser(description="Deletes file.")
    parser.add_argument(
        "--key", type=str, help="key of the file to delete", required=True
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="When provided, deletes the requested file on the cloud service as well.",
    )
    args = parser.parse_args()

    dm.delete(
        key=args.key, local=True, remote=args.remote,
    )
