# -*- coding: utf-8 -*-
from pathlib import Path
from pydantic_settings import (BaseSettings, SettingsConfigDict)

# Constants
MISSING_ENV = '>>> missing ENV value <<<'
""" Error message for missing values in the .env file. """


# -----------------------------------------------------------------------------
#
class CommonConfig(BaseSettings):
    """ Configuration parameters used by all environments.

    These values are populated in the following order; content of the
    .env file.
    """
    model_config = SettingsConfigDict(env_file_encoding='utf-8',
                                      env_file=Path(__file__).parent / '.env')
    # project
    name: str = MISSING_ENV
    version: str = MISSING_ENV
    service_name: str = MISSING_ENV

    log_level: str = MISSING_ENV

    # External resource parameters.
    mongo_url: str = MISSING_ENV
    rabbit_url: str = MISSING_ENV
    service_api_key: str = MISSING_ENV
    flower_host: str = MISSING_ENV


config = CommonConfig()
