from abc import abstractclassmethod
from tqdm import tqdm


class Provider:
    @abstractclassmethod
    def download(self, key):
        raise NotImplementedError

    @abstractclassmethod
    def upload(self, key, file_path):
        raise NotImplementedError

    @abstractclassmethod
    def list_files(self):
        raise NotImplementedError

    @abstractclassmethod
    def check_valid(self, key, file_path):
        raise NotImplementedError

    @abstractclassmethod
    def file_size(self, key):
        raise NotImplementedError

    @property
    def files(self):
        return self.list_files()


class Progress:
    def __init__(self, size, key):
        self.progress_bar = tqdm(desc=f"Downloading {key}", total=size)

    def __call__(self, bytes):
        self.progress_bar.update(bytes)

    def __exit__(self):
        self.progress_bar.close()
