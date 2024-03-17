# -*- coding: utf-8 -*-
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import (BaseSettings, SettingsConfigDict)
import os


# Constants
MISSING_ENV = '>>> missing ENV value <<<'
""" Error message for missing values in the .env file. """

"""
BUILD_ENV = os.getenv("BUILD_ENV", "dev")

if BUILD_ENV == "dev":
    ENV_FILE_PATH = Path(__file__).parent / '.env.dev'
else:
    ENV_FILE_PATH = Path(__file__).parent / '.env'

load_dotenv(ENV_FILE_PATH)
"""


class CommonConfig(BaseSettings):
    """ Configuration parameters used by all environments.

    These values are populated in the following order; content of the
    .env file.
    """

    # project
    name: str = os.getenv("NAME", MISSING_ENV)
    version: str = os.getenv("VERSION", MISSING_ENV)
    service_name: str = os.getenv("SERVICE_NAME", MISSING_ENV)

    log_level: str = MISSING_ENV

    # External resource parameters.
    redis_url: str = os.getenv("REDIS_URL", MISSING_ENV)
    mongo_url: str = os.getenv("MONGO_URL", MISSING_ENV)
    rabbit_url: str = os.getenv("RABBIT_URL", MISSING_ENV)
    service_api_key: str = os.getenv("SERVICE_API_KEY", MISSING_ENV)
    database_name: str = os.getenv("DATABASE_NAME", MISSING_ENV)


config = CommonConfig()
