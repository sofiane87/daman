from pathlib import Path
from configparser import ConfigParser

from daman.configure import CONFIG_DIR


CONFIG = ConfigParser()
CONFIG.read(CONFIG_DIR / "config")
DATA_FOLDER = Path(CONFIG["local"]["data_dir"])
