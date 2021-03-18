import logging
from daman.configure import HOME_DIR, CONFIG_DIR, CLOUD_SERVICES
from daman.data_manager import DataManager

logging.basicConfig(level=logging.INFO)

daman = DataManager()
