import os
import joblib
import psutil
from io import BytesIO
from pathlib import Path
from warnings import warn
from os.path import getsize
from datetime import datetime
from logging import getLogger

from data_manager import CONFIG, DATA_FOLDER, DataRegistery
from data_manager.utils import dir_size
from data_manager.services import current_service

logger = getLogger(__name__)

REGISTERY = DataRegistery()
SERVICE = current_service()

DATA_FOLDER.mkdir(parents=True, exist_ok=True)


def pull(
    key: str,
    force_download: bool = False,
    persist: bool = None,
    memory_only: bool = False,
):
    msg = f"key '{key}' not found"
    assert key in SERVICE.keys, msg
    if key in REGISTERY:
        if persist is not None:
            REGISTERY[key]["persist"] = persist
        REGISTERY[key]["used"] += 1
        REGISTERY[key]["last_used"] = datetime.now()
        file_path = Path(REGISTERY[key]["path"])
        is_valid = SERVICE.check_valid(key=key, file_path=file_path)
        if is_valid:
            obj = joblib.load(file_path)
            return obj["data"], obj["meta"]
        else:
            warn(
                f"local '{key}' file doesn't match remote. Data will be downloaded again."
            )

    # download file
    if persist is None:
        persist = False

    if memory_only:
        buffer = BytesIO()
        SERVICE.download(key=key, buffer=buffer)
        obj = joblib.load(buffer)
        return obj["data"], obj["meta"]
    else:
        clear_disc(key=key)
        file_path = (Path(DATA_FOLDER) / key).resolve()
        SERVICE.download(key=key, file_path=file_path)
        REGISTERY[key] = {
            "path": str(file_path),
            "used": 1,
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "size": getsize(str(file_path)),
            "persist": persist,
        }
        obj = joblib.load(file_path)
        return obj["data"], obj["meta"]


def push(
    obj: object,
    key: str,
    meta: object = None,
    force: bool = False,
    persist: bool = False,
):
    obj = {"data": obj, "meta": meta}
    if key in SERVICE.keys:
        if force:
            warn(f"`{key}` already in use and will be over-written.")
        else:
            raise KeyError(
                f"`{key}` already in use. Please choose a different key or use --force to enforce key override."
            )

    # store locally
    file_path = (Path(DATA_FOLDER) / key).resolve()
    # store locally
    joblib.dump(obj, file_path)

    # upload to cloud
    SERVICE.upload(key=key, file_path=file_path)

    # update registery
    REGISTERY[key] = {
        "path": str(file_path),
        "used": 1,
        "created_at": datetime.now(),
        "last_used": datetime.now(),
        "size": getsize(str(file_path)),
        "persist": persist,
    }


def delete(key: str, local: bool = True, remote: bool = False):
    if local:
        item = REGISTERY[key]
        # delete file
        del REGISTERY[key]
        # delete local file
        os.remove(item["path"])
    if remote:
        # delete remote file
        SERVICE.delete(key=key)


def list_data(local_only: bool = False):
    return [
        {
            "key": key,
            "local": key in REGISTERY,
            "size": SERVICE.file_size(key) // 2 ** 20,
            "remote": key in SERVICE.keys,
        }
        for key in (
            REGISTERY.keys if local_only else set(SERVICE.keys) | set(REGISTERY.keys)
        )
    ]


def available_disc():
    if CONFIG["local"]["allocated_space"] is None:
        free_space = (
            psutil.disk_usage(DATA_FOLDER).free() // 2 ** 20
        )  # disc space in megabytes
    else:
        free_space = int(CONFIG["local"]["allocated_space"]) - dir_size(DATA_FOLDER)
    return free_space


def clear_disc(key: str = None, space: int = None, ignore_persist: bool = False):
    if key is not None:
        file_size = SERVICE.file_size(key=key) // 2 ** 20
    else:
        file_size = space

    while available_disc() < file_size:
        items = sorted(
            REGISTERY.items,
            key=lambda x: (x[1]["persist"], x[1]["last_used"], x[1]["used"]),
        )

        if len(items) > 0:
            del_key, del_item = items[0]
            if not del_item["persist"] or ignore_persist:
                delete(key=del_key)
                continue

        raise IOError(
            f"Not enough space available. Only {available_disc()} MB available but {file_size} MB required. No additional file can be deleted."
        )
