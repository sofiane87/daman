import argparse
from pathlib import Path

from daman import CONFIG_DIR
from daman.services import PROVIDERS
from daman.configure import configure


def configure_command():
    parser = argparse.ArgumentParser(description="Sets up daman package.")
    parser.add_argument(
        "--storage_name",
        type=str,
        help="name of the storage to push to and pull from",
        required=True,
    )
    parser.add_argument(
        "--service",
        type=str,
        help="type of cloud provider used",
        required=True,
        choices=list(PROVIDERS.keys()),
    )
    parser.add_argument(
        "--local_dir",
        type=Path,
        help="local directory to store data at",
        default=(CONFIG_DIR / "data"),
    )
    parser.add_argument(
        "--allocated_space",
        type=int,
        default=None,
        help="disc space allocated to local directory",
    )
    args = parser.parse_args()

    configure(
        storage_name=args.storage_name,
        service=args.service,
        local_dir=args.local_dir,
        allocated_space=args.allocated_space,
    )
