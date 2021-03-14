from typing import Union
from pathlib import Path
from os.path import getsize

unit_map = {None: 2 ** 0, "K": 2 ** 10, "M": 2 ** 20, "G": 2 ** 30}


def dir_size(dir: Union[str, Path], unit="M"):
    msg = f"unit '{unit}' not recognized. Allowed units: [{list(unit_map.keys())}]"
    assert unit in unit_map, msg

    dir_size = 0
    for file in Path(dir).rglob("*"):
        if file.is_file():
            dir_size += getsize(dir)

    return dir_size // unit_map[unit]
