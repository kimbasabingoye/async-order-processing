# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-03-30 12:13:57
     $Rev: 47
"""

# BUILTIN modules
from typing import List

# Third party modules
from pydantic import UUID4
from fastapi import HTTPException, Depends, APIRouter
from kombu.exceptions import OperationalError
from fastapi.responses import Response
from fastapi import APIRouter, status
from loguru import logger

# Local modules
from .customer_api_adapter import CustomersApi
# from .documentation import customer_id_documentation
from .customer_data_adapter import CustomersRepository
from .models import (CustomerCreateModel, CustomerModel, CustomersCollection,
                     NotFoundError, FailedUpdateError, ConnectError)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.customers_tasks import create_customer_processor, read_customer_processor, list_customers_processor

# Constants
ROUTER = APIRouter(prefix=f"/v1/customers", tags=[f"Customers"])
""" Customer API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post('',
             status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
async def create_customer(payload: CustomerCreateModel) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    payload_json = payload.model_dump()
    try:
        # Add payload message to Celery for processing.
        result = create_customer_processor.delay(payload_json)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.get('{/customer_id}',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def get_customer(customer_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = read_customer_processor.delay(customer_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.get('',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def list_customers() -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = list_customers_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
