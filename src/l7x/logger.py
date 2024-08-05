#####################################################################################################

from json import load as _load_json
from logging import INFO, Logger, captureWarnings, getLogger
from os import getenv
from os.path import exists as _is_path_exists
from typing import Final

from coloredlogs import install as _coloredlogs_install

#####################################################################################################

DEFAULT_LOGGER_NAME = 'l7x'

#####################################################################################################

def setup_logging(
    *,
    default_path: str = 'logging.json',
    default_level: int = INFO,
    env_key: str = 'L7X_LOG_CFG',
) -> Logger:
    captureWarnings(True)
    logger: Final = getLogger(DEFAULT_LOGGER_NAME)

    config: dict[str, str | dict[str, str]] = {}
    log_config_path = getenv(env_key, default_path)
    if _is_path_exists(log_config_path):
        logger.info(f'Loading logging configuration from {log_config_path}')
        with open(log_config_path, encoding='utf-8') as config_file:
            config = _load_json(config_file)

    default_log_level: Final = config.get('default', default_level)
    _coloredlogs_install(level=default_log_level, milliseconds=True)

    if 'specific' in config:
        specific: Final = config.get('specific', {})
        if isinstance(specific, dict):
            for log_name, log_level in specific.items():
                getLogger(log_name).setLevel(log_level)

    return logger

#####################################################################################################
