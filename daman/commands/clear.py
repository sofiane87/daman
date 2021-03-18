import argparse
from daman import daman as dm


def clear_command():
    parser = argparse.ArgumentParser(description="Clears disc space in local storage.")
    parser.add_argument(
        "--space",
        type=int,
        help="Amount of disc space in MegaBytes to clear.",
        required=True,
    )
    parser.add_argument(
        "--ignore-persist",
        action="store_true",
        help="When provided, deletes the requested file on the cloud service as well.",
    )
    args = parser.parse_args()

    dm.clear_disc(space=args.space, force=args.ignore_persist)
