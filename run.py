#!/usr/bin/env python


# Third party modules
import uvicorn

# Local modules
from src.main import app
from src.config.setup import config

if __name__ == "__main__":
    uv_config = {
        'app': 'src.main:app',
        'log_level': config.log_level,
        'host': '0.0.0.0',
        'port': 8000,
        'reload': True}
    uvicorn.run(**uv_config)
