from pathlib import Path
from logging import getLogger
from configparser import ConfigParser


logger = getLogger(__name__)

HOME = Path().home()
AWS_DIR = HOME / ".aws"


def configure_aws(
    access_key_id: str, secret_access_key: str, region: str = None
) -> None:
    """Short summary.

    Parameters
    ----------
    access_key_id : str
        Description of parameter `access_key_id`.
    secret_access_key : str
        Description of parameter `secret_access_key`.
    region : str
        Description of parameter `region`.

    Returns
    -------
    None
        Description of returned object.

    """
    AWS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"updating AWS credentials: {AWS_DIR / 'credentials'}")

    aws_credentials = ConfigParser()
    if (AWS_DIR / "credentials").exists():
        with (AWS_DIR / "credentials").open("r") as fr:
            aws_credentials.read_file(fr)

    for key, value in [
        ("aws_access_key_id", access_key_id),
        ("aws_secret_access_key", secret_access_key),
    ]:
        set_value(aws_credentials, key, value)

    with (AWS_DIR / "credentials").open("w") as fw:
        aws_credentials.write(fw)

    if region is not None:
        logger.info(f"updating AWS config: {AWS_DIR / 'config'}")
        aws_config = ConfigParser()
        if (AWS_DIR / "config").exists():
            with (AWS_DIR / "config").open() as fr:
                aws_config.read_file(fr)

        set_value(aws_config, "region", region)

        with (AWS_DIR / "config").open("w") as fw:
            aws_config.write(fw)


def set_value(config, key, value):
    """Short summary.

    Parameters
    ----------
    config : type
        Description of parameter `config`.
    key : type
        Description of parameter `key`.
    value : type
        Description of parameter `value`.

    Returns
    -------
    type
        Description of returned object.

    """
    if not config.has_section("default"):
        config.add_section("default")

    if config.has_option("default", value):
        if value != config[f"default_{key}", value]:
            logger.warning(
                f"'{key}' already defined and will be changed from '{config[f'default.{key}']}' to '{value}'"
            )
        else:
            logger.info(f"'{key}' set to '{value}'")

    config.set("default", key, value)
