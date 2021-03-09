from abc import abstractclassmethod
from tqdm import tqdm


class Provider:
    @abstractclassmethod
    def download(self, file_name):
        raise NotImplementedError

    @abstractclassmethod
    def upload(self, file_name, obj):
        raise NotImplementedError

    @abstractclassmethod
    def list_files(self):
        raise NotImplementedError

    @abstractclassmethod
    def check_valid(self, file_name):
        raise NotImplementedError

    @abstractclassmethod
    def file_size(self, file_name):
        raise NotImplementedError

    @property
    def files(self):
        return self.list_files()


class Progress:
    def __init__(self, size, file_name):
        self.progress_bar = tqdm(desc=f"Downloading {file_name}", total=size)

    def __call__(self, bytes):
        self.progress_bar.update(bytes)

    def __exit__(self):
        self.progress_bar.close()
