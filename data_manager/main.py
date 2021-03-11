import json
import boto3
import joblib
import hashlib
from logging import getLogger

from data_manager import CONFIG, DATA_FOLDER, DataRegistery

logger = getLogger(__name__)

REGISTERY = DataRegistery()


def get_data(name, force_download=False, required=False):
    pass


def upload_data(obj, name, meta=None):
    obj = {"data": obj, "meta": meta}
    pass


def delete_data(name):
    pass


def list_data(local_only=False):
    pass


def clear(space=None):
    pass
