import boto3
from pathlib import Path
from logging import getLogger
from typing import Union, IO, AnyStr

from daman.services import Provider, Progress


logger = getLogger(__name__)


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
                Fileobj=buffer, Key=key, Bucket=self.bucket, Callback=pbar,
            )
        else:
            raise ValueError("`buffer` or `file_path` cannot be `None` simultaneously.")

        # close progress bar
        pbar.close()

    def upload(
        self, key: str, file_path: Union[str, Path] = None, buffer: IO[AnyStr] = None
    ):
        if file_path is not None:
            msg = f"{file_path} does not exist."
            assert file_path.exists(), msg
            # Initialising progress bar
            pbar = Progress(size=20, key=key)

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
        elif buffer is not None:
            # Initialising progress bar
            pbar = Progress(size=buffer.getbuffer().nbytes, key=key)
            # Upload to bucket
            self.s3.meta.client.upload_fileobj(
                Fileobj=buffer,
                Key=key,
                Bucket=self.bucket,
                Callback=pbar,
                ExtraArgs={"Metadata": {"md5": self.md5(buffer=buffer)}},
            )

            # close progres bar
            pbar.close()
        else:
            msg = "either `file_path` or `buffer` must be provided."
            raise ValueError(msg)

    def delete(self, key: str):
        if key in self.keys:
            self.s3.meta.client.delete_object(Bucket=self.bucket, Key=key)
        else:
            logger.warning(f"`{key}` already deleted from cloud service.")

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
            logger.warning(msg)
            return True
