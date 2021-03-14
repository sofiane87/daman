import json

from data_manager import CONFIG_DIR


class DataRegistery:
    def __init__(self):
        self.registery_path = CONFIG_DIR / "data_registery.json"

    def read(self):
        if self.registery_path.exists():
            with self.registery_path.open("r") as fr:
                return json.load(fr)
        return {}

    def write(self, registery):
        with self.registery_path.open("w") as fw:
            json.dump(obj=registery, fp=fw)

    def __getitem__(self, key):
        registery = self.read()

        return registery[key]

    def __setitem__(self, key, value):
        registery = self.read()

        registery[key] = value
        self.write(registery)

    def __delitem__(self, key, value):
        registery = self.read()

        del registery[key]

        self.write(registery)

    @property
    def keys(self):
        return list(self.read().keys())

    @property
    def values(self):
        return list(self.read().values())

    @property
    def items(self):
        return list(self.read().items())

    def __contains__(self, item):
        registery = self.read()
        return item in registery
