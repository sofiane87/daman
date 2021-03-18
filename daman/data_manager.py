import os
import joblib
import psutil
from io import BytesIO
from pathlib import Path
from warnings import warn
from os.path import getsize
from datetime import datetime

from daman.utils import dir_size
from configparser import ConfigParser

from daman.configure import CONFIG_DIR
from daman.services import PROVIDERS
from daman.data import DataRegistery


class DataManager:
    @property
    def config(self):
        config = ConfigParser()
        config.read(CONFIG_DIR / "config")
        return config

    @property
    def data_folder(self):
        config = self.config
        d_folder = Path(config["local"]["data_dir"])
        if not d_folder.exists():
            d_folder.mkdir(parents=True, exist_ok=True)
        return d_folder

    @property
    def registery(self):
        return DataRegistery()

    @property
    def service(self):
        req_service = self.config["service"]["service"]
        if req_service in PROVIDERS:
            return PROVIDERS[req_service](config=self.config)
        else:
            raise KeyError(
                f"service `{req_service}` requested is not available among provided services."
            )

    def pull(
        self,
        key: str,
        force: bool = False,
        persist: bool = None,
        memory_only: bool = False,
    ):
        msg = f"key '{key}' not found"
        assert key in self.service.keys, msg
        if key in self.registery and not force:
            if persist is not None:
                self.registery[key]["persist"] = persist
            self.registery[key]["used"] += 1
            self.registery[key]["last_used"] = datetime.now()
            file_path = Path(self.registery[key]["path"])
            is_valid = self.service.check_valid(key=key, file_path=file_path)
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
            self.service.download(key=key, buffer=buffer)
            obj = joblib.load(buffer)
            return obj["data"], obj["meta"]
        else:
            self.clear_disc(key=key)
            file_path = (Path(self.data_folder) / key).resolve()
            self.service.download(key=key, file_path=file_path)
            self.registery[key] = {
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
        self,
        obj: object,
        key: str,
        meta: object = None,
        force: bool = False,
        persist: bool = False,
    ):
        obj = {"data": obj, "meta": meta}
        if key in self.service.keys:
            if force:
                warn(f"`{key}` already in use and will be over-written.")
            else:
                raise KeyError(
                    f"`{key}` already in use. Please choose a different key or use --force to enforce key override."
                )

        # store locally
        file_path = (Path(self.data_folder) / key).resolve()
        # store locally
        joblib.dump(obj, file_path)

        # upload to cloud
        self.service.upload(key=key, file_path=file_path)

        # update registery
        self.registery[key] = {
            "path": str(file_path),
            "used": 1,
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "size": getsize(str(file_path)),
            "persist": persist,
        }

    def delete(self, key: str, local: bool = True, remote: bool = False):
        if local:
            item = self.registery[key]
            # delete file
            del self.registery[key]
            # delete local file
            os.remove(item["path"])
        if remote:
            # delete remote file
            self.service.delete(key=key)

    def list_data(self, local_only: bool = False):
        return [
            {
                "key": key,
                "local": key in self.registery,
                "size": self.service.file_size(key) // 2 ** 20,
                "remote": key in self.service.keys,
            }
            for key in (
                self.registery.keys
                if local_only
                else set(self.service.keys) | set(self.registery.keys)
            )
        ]

    def available_disc(self):
        if self.config["local"]["allocated_space"] is None:
            free_space = (
                psutil.disk_usage(self.data_folder).free() // 2 ** 20
            )  # disc space in megabytes
        else:
            free_space = int(self.config["local"]["allocated_space"]) - dir_size(
                self.data_folder
            )
        return free_space

    def clear_disc(
        self, key: str = None, space: int = None, ignore_persist: bool = False
    ):
        if key is not None:
            file_size = self.service.file_size(key=key) // 2 ** 20
        else:
            file_size = space

        while self.available_disc() < file_size:
            items = sorted(
                self.registery.items,
                key=lambda x: (x[1]["persist"], x[1]["last_used"], x[1]["used"]),
            )

            if len(items) > 0:
                del_key, del_item = items[0]
                if not del_item["persist"] or ignore_persist:
                    self.delete(key=del_key)
                    continue

            raise IOError(
                f"Not enough space available. Only {self.available_disc()} MB available but {file_size} MB required. No additional file can be deleted."
            )
