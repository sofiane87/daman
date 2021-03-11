import boto3
import hashlib
from os.path import getsize

from data_manager import CONFIG
from data_manager.services import Provider, Progress


class AWSProvider(Provider):
    def __init__(self):
        self.bucket = CONFIG["service"]["name"]
        self.s3 = boto3.resource("s3")

    @classmethod
    def download(self, key, store_path):
        # Checking file exists
        msg = f"{key} does not exist in `{self.bucket}` S3 bucket."
        assert key in self.files, msg

        # Initialising progress bar
        pbar = Progress(size=self.file_size(key), key=key)

        # Download
        self.s3.meta.client.download_file(
            Bucket=self.bucket, Key=key, FileName=store_path, Callback=pbar,
        )

        # close progress bar
        del pbar

    @classmethod
    def upload(self, key, file_path):
        msg = f"{file_path} does not exist."
        assert file_path.exists(), msg
        # Initialising progress bar
        pbar = Progress(size=getsize(file_path), key=key)

        # Upload to bucket
        self.s3.meta.client.download_file(
            Bucket=self.bucket,
            Key=key,
            FileName=file_path,
            Callback=pbar,
            ExtraArgs={"Metadata": {"md5": hashlib.md5(file_path).hexdigest()}},
        )

        # close progres bar
        del pbar

    @classmethod
    def list_files(self):
        return [file.key for file in self.s3.Bucket(self.bucket)]

    @classmethod
    def file_size(self, key):
        return self.s3.Bucket(self.bucket).Object(key).content_length

    @classmethod
    def check_valid(self, key, file_path):
        # get local etag
        msg = f"{file_path} does not exist."
        assert file_path.exists(), msg
        local_md5 = hashlib.md5(file_path).hexdigest()
        # get remote etag
        msg = f"{key} is not available on `{self.bucket}` S3 bucket."
        assert key in self.files
        remote_md5 = self.s3.Bucket(self.bucket).Object(key).metadata["md5"]
        return local_md5 == remote_md5
