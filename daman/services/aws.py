import boto3
from pathlib import Path
from warnings import warn
from os.path import getsize
from typing import Union, IO, AnyStr

from daman.services import Provider, Progress


class AWSProvider(Provider):
    def __init__(self, config):
        self.bucket = config["service"]["name"]
        self.s3 = boto3.resource("s3")

    def download(
        self, key: str, file_path: Union[str, Path] = None, buffer: IO[AnyStr] = None
    ):
        # Checking file exists
        msg = f"{key} does not exist in `{self.bucket}` S3 bucket."
        assert key in self.keys, msg

        # Initialising progress bar
        pbar = Progress(size=self.file_size(key), key=key)

        # Download
        if file_path is not None:
            self.s3.meta.client.download_file(
                Bucket=self.bucket, Key=key, Filename=str(file_path), Callback=pbar,
            )
        elif buffer is not None:
            self.s3.meta.client.download_fileobj(
                Bucket=self.bucket, Key=key, Fileobj=buffer, Callback=pbar,
            )
        else:
            raise ValueError("`buffer` or `file_path` cannot be `None` simultaneously.")

        # close progress bar
        pbar.close()

    def upload(self, key: str, file_path: Union[str, Path]):
        msg = f"{file_path} does not exist."
        assert file_path.exists(), msg
        # Initialising progress bar
        pbar = Progress(size=getsize(file_path), key=key)

        # Upload to bucket
        self.s3.meta.client.upload_file(
            Bucket=self.bucket,
            Key=key,
            Filename=str(file_path),
            Callback=pbar,
            ExtraArgs={"Metadata": {"md5": self.md5(file_path=file_path)}},
        )

        # close progres bar
        pbar.close()

    def delete(self, key: str):
        self.s3.meta.client.delete_object(Bucket=self.bucket, Key=key)

    @property
    def keys(self):
        return [file.key for file in self.s3.Bucket(self.bucket).objects.all()]

    def file_size(self, key: str):
        return self.s3.Bucket(self.bucket).Object(key).content_length

    def check_valid(self, key: str, file_path: Union[str, Path]):
        # get local etag
        msg = f"{file_path} does not exist."
        assert file_path.exists(), msg
        local_md5 = self.md5(file_path=file_path)
        # get remote etag
        msg = f"{key} is not available on `{self.bucket}` S3 bucket."
        if key in self.keys:
            remote_md5 = self.s3.Bucket(self.bucket).Object(key).metadata["md5"]
            return local_md5 == remote_md5
        else:
            warn(msg)
            return True
