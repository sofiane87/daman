from daman import CONFIG
from daman.services.base import Provider, Progress
from daman.services.aws import AWSProvider

PROVIDERS = {"aws": AWSProvider}


def current_service():
    req_service = CONFIG["service"]["service"]
    if req_service in PROVIDERS:
        return PROVIDERS[req_service]()
    else:
        raise KeyError(
            f"service `{req_service}` requested is not available among provided services."
        )
