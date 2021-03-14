import hashlib
from tqdm import tqdm
from pathlib import Path
from typing import Union, IO, AnyStr
from abc import abstractmethod, abstractproperty


class Provider:
    @abstractmethod
    def download(
        self, key: str, file_path: Union[str, Path] = None, buffer: IO[AnyStr] = None
    ):
        raise NotImplementedError

    @abstractmethod
    def upload(
        self, key: str, file_path: Union[str, Path] = None, buffer: IO[AnyStr] = None
    ):
        raise NotImplementedError

    @abstractproperty
    def keys(self):
        raise NotImplementedError

    @abstractmethod
    def check_valid(self, key: str, file_path: Union[str, Path]):
        raise NotImplementedError

    @abstractmethod
    def file_size(self, key: str):
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str):
        raise NotImplementedError

    def md5(self, file_path: Union[str, Path] = None, buffer: IO[AnyStr] = None):
        md5_hash = hashlib.md5()

        if file_path is not None:
            buffer = Path(file_path).open("rb")

        msg = f"`buffer` and `file_path` cannot be `None` simultaneously."
        assert buffer is not None, msg

        content = buffer.read()
        md5_hash.update(content)
        return md5_hash.hexdigest()


class Progress:
    def __init__(self, size: int, key: str):
        self.progress_bar = tqdm(desc=f"Downloading {key}", total=size)

    def __call__(self, bytes: int):
        self.progress_bar.update(bytes)

    def __exit__(self):
        self.progress_bar.close()
