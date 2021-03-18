import argparse
from daman import daman as dm


def download_command(parser):
    parser = argparse.ArgumentParser(description="Sets up daman package.")
    parser.add_argument(
        "--key", type=str, help="key of the file to delete", required=True, choices=[]
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="When provided forces the download even if the file is already available.",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="When provided ensures that the downloaded file is always kept on disc on manually deleted.",
    )
    args = parser.parse_args()

    dm.pull(key=args.key, local=True, force_download=args.force, persist=args.persist)
