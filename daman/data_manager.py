import os
import joblib
import psutil
import pandas as pd
from io import BytesIO
from logging import getLogger
from pathlib import Path
from os.path import getsize
from datetime import datetime

from daman.utils import dir_size
from configparser import ConfigParser

from daman.configure import CONFIG_DIR
from daman.services import PROVIDERS
from daman.data import DataRegistery


logger = getLogger(__name__)


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
            if not is_valid:
                logger.warning(
                    f"local '{key}' file doesn't match remote version. Please pull it again using `force`."
                )
            logger.info(f"data `{key}` available locally.")
            obj = joblib.load(file_path)
            return obj["data"], obj["meta"]

        # download file
        if persist is None:
            persist = False

        if memory_only:
            with BytesIO() as buffer:
                buffer.seek(0)
                self.service.download(key=key, buffer=buffer)
                obj = joblib.load(buffer)
                return obj["data"], obj["meta"]
        else:
            logger.info(f"downloading `{key}` file.")
            self.clear_disc(key=key)
            file_path = (self.data_folder / key).resolve()
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
        local: bool = True,
        force: bool = False,
        persist: bool = False,
    ):
        obj = {"data": obj, "meta": meta}
        if key in self.service.keys:
            if force:
                logger.warning(f"`{key}` already in use and will be over-written.")
            else:
                err_msg = f"`{key}` already in use. Please choose a different key or use --force to enforce key override."
                logger.error(err_msg)
                raise KeyError(err_msg)

        with BytesIO() as file_buffer:
            joblib.dump(obj, file_buffer)
            # reset buffer pointer
            file_buffer.seek(0)

            if local:
                logger.info(f"ensuring disc space available")
                self.clear_disc(space=file_buffer.getbuffer().nbytes / 2 ** 20)

                logger.info(f"storing `{key}` data locally.")
                # store locally
                file_path = (self.data_folder / key).resolve()
                with file_path.open("wb") as fw:
                    fw.write(file_buffer.read())

                logger.info(f"uploading {key} to cloud service.")
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
            else:
                logger.info(f"uploading {key} to cloud service.")
                # upload to cloud
                self.service.upload(key=key, buffer=file_buffer)

    def delete(self, key: str, local: bool = True, remote: bool = False):
        if local:
            logger.info(f"deleting `{key}` data locally.")
            item = self.registery[key]
            # delete file
            del self.registery[key]
            # delete local file
            os.remove(item["path"])
        if remote:
            logger.info(f"deleting `{key}` data on cloud service.")
            # delete remote file
            self.service.delete(key=key)

    @property
    def summary(self):
        service_keys = list(self.service.keys)
        return pd.DataFrame(
            [
                {
                    "key": key,
                    "local": key in self.registery,
                    "remote": key in service_keys,
                    "size (MB)": round(
                        (
                            self.registery[key]["size"]
                            if key in self.registery.keys
                            else self.service.file_size(key)
                        )
                        / 2 ** 20,
                        2,
                    ),
                }
                for key in (set(self.service.keys) | set(self.registery.keys))
            ]
        )

    def available_disc(self):
        if self.config["local"]["allocated_space"] is None:
            free_space = (
                psutil.disk_usage(self.data_folder).free() / 2 ** 20
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
            file_size = self.service.file_size(key=key) / 2 ** 20
        else:
            file_size = space

        while self.available_disc() < file_size:
            logger.info(
                f"deleting `{file_size - self.available_disc()}` data on cloud service."
            )
            items = sorted(
                self.registery.items,
                key=lambda x: (x[1]["persist"], x[1]["last_used"], x[1]["used"]),
            )

            if len(items) > 0:
                del_key, del_item = items[0]
                if not del_item["persist"] or ignore_persist:
                    self.delete(key=del_key, local=True, remote=False)
                    continue

            raise IOError(
                f"Not enough space available. Only {self.available_disc()} MB available but {file_size} MB required. No additional file can be deleted."
            )
