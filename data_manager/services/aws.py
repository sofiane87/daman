import boto3
import joblib
import hashlib
from pathlib import Path
from os.path import getsize
from configparser import ConfigParser

from data_manager.configure import CONFIG_DIR
from data_manger.services.base import Provider, Progress

CONFIG = ConfigParser()
CONFIG.read(CONFIG_DIR / "config")


class AWSProvider(Provider):
    bucket = CONFIG["service"]["name"]
    data_folder = Path(CONFIG["local"]["data_dir"])
    s3 = boto3.resource("s3")

    @classmethod
    def download(self, file_name):
        # Checking file exists
        msg = f"{file_name} does not exist in `{self.bucket}` S3 bucket."
        assert file_name in self.files, msg

        # Initialising progress bar
        pbar = Progress(size=self.file_size(file_name), file_name=file_name)

        # Download
        self.s3.meta.client.download_file(
            Bucket=self.bucket,
            Key=file_name,
            FileName=str(self.data_folder / file_name),
            Callback=pbar,
        )

        # close progress bar
        del pbar

    @classmethod
    def upload(self, file_name, obj):
        # Store locally
        full_path = str(self.data_folder / file_name)
        joblib.dump(obj, full_path)

        # Initialising progress bar
        pbar = Progress(size=getsize(full_path), file_name=file_name)

        # Upload to bucket
        self.s3.meta.client.download_file(
            Bucket=self.bucket,
            Key=file_name,
            FileName=full_path,
            Callback=pbar,
            ExtraArgs={"Metadata": {"md5": hashlib.md5(full_path).hexdigest()}},
        )

        # close progres bar
        del pbar

    @classmethod
    def list_files(self):
        return [file.key for file in self.s3.Bucket(self.bucket)]

    @classmethod
    def file_size(self, file_name):
        return self.s3.Bucket(self.bucket).Object(file_name).content_length

    @classmethod
    def check_valid(self, file_name):
        # get local etag
        local_file = self.data_folder / file_name
        msg = f"{local_file} does not exist."
        assert local_file.exists(), msg
        local_md5 = hashlib.md5(str(self.data_folder / file_name)).hexdigest()
        # get remote etag
        assert file_name in self.files
        remote_md5 = self.s3.Bucket(self.bucket).Object(file_name).metadata["md5"]
        return local_md5 == remote_md5
