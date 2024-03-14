# BUILTIN modules
from typing import Any
from pathlib import Path

# Third party modules
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# local modules
from .config.setup import config
from .api import process_routes, health_route
from .api.customers.router import router as customers_router
from .api.employees.router import ROUTER as employees_router
from .api.orders.router import router as orders_router
from .api.quotations.router import ROUTER as quotations_router
from .api.realisations.router import ROUTER as realisations_router
from .api.documentation import (license_info, tags_metadata, description)


# -----------------------------------------------------------------------------
#
class Service(FastAPI):
    """
    This class adds router and image handling for the OpenAPI documentation
    as well as unified logging.


    @type logger: C{loguru.logger}
    @ivar logger: logger object instance.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, *args: Any, **kwargs: Any):
        """ The class constructor.

        :param args: named arguments.
        :param kwargs: key-value pair arguments.
        """

        super().__init__(*args, **kwargs)

        # Needed for OpenAPI Markdown images to be displayed.
        static_path = Path(__file__).parent / 'design'
        self.mount("/static", StaticFiles(directory=static_path))

        # Add declared router information (note that
        # the order is related to the documentation order).
        self.include_router(process_routes.ROUTER)
        self.include_router(health_route.ROUTER)
        self.include_router(customers_router)
        self.include_router(employees_router)
        self.include_router(orders_router)
        self.include_router(quotations_router)
        self.include_router(realisations_router)


# ---------------------------------------------------------
# Instantiate the service.
app = Service(
    redoc_url=None,
    title=config.name,
    version=config.version,
    description=description,
    license_info=license_info,
    openapi_tags=tags_metadata,
)
