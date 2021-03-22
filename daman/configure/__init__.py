from typing import Union
from pathlib import Path
from configparser import ConfigParser

from daman.configure.aws import configure_aws


HOME_DIR = Path().home()
CONFIG_DIR = HOME_DIR / ".daman"
CLOUD_SERVICES = {"aws": configure_aws}


def configure(
    storage_name: str,
    service: str,
    local_dir: Union[Path, str] = None,
    allocated_space: int = None,
    service_settings: dict = None,
) -> None:
    """Short summary.

    Parameters
    ----------
    storage_name : str
        Description of parameter `storage_name`.
    service : str
        Description of parameter `service`.
    local_dir : Union[Path, str]
        Description of parameter `local_dir`.
    allocated_space : int
        Description of parameter `allocated_space`.
    service_settings : dict
        Description of parameter `service_settings`.

    Returns
    -------
    None
        Description of returned object.

    """

    dm_config = ConfigParser(allow_no_value=True)
    # storing service config
    dm_config.add_section("service")
    dm_config["service"] = {"service": service, "name": storage_name}
    # storing local config
    dm_config.add_section("local")
    if local_dir is None:
        local_dir = str((CONFIG_DIR / "data").resolve())

    dm_config["local"] = {
        "data_dir": str(Path(local_dir).resolve()),
        "registery": str(CONFIG_DIR / "registery.json"),
    }

    if allocated_space is not None:
        dm_config["local"]["allocated_space"] = allocated_space

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with (CONFIG_DIR / "config").open("w") as fw:
        dm_config.write(fw)

    if service_settings is not None:
        configure_service(service=service, settings=service_settings)


def configure_service(service: str, settings: dict) -> None:
    """Short summary.

    Parameters
    ----------
    service : str
        Description of parameter `service`.
    settings : dict
        Description of parameter `settings`.

    Returns
    -------
    None
        Description of returned object.

    """
    service = service.lower()

    # check service is supported
    assert_msg = f"'{service}' is not currently supported. Available services: {list(CLOUD_SERVICES.keys())}"
    assert service in CLOUD_SERVICES, assert_msg

    # call config function
    config_func = CLOUD_SERVICES[service]
    config_func(**settings)
