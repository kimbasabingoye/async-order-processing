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
from .order_api_adapter import OrdersApi
# from .documentation import order_id_documentation
from .order_data_adapter import OrdersRepository
from .models import (OrderCreateModel, OrderModel,
                     NotFoundError, FailedUpdateError, ConnectError)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.orders_tasks import create_order_processor, read_order_processor, list_orders_processor, cancel_order_processor, validate_order_processor, reject_order_processor

# Constants
ROUTER = APIRouter(prefix=f"/v1/orders", tags=[f"Orders"])
""" Order API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post('',
             status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
def create_order(payload: OrderCreateModel) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    # payload_json = OrderCreateModel(**payload.model_dump()).model_dump()
    payload_json = payload.model_dump()
    try:
        # Add payload message to Celery for processing.
        result = create_order_processor.delay(payload_json)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
    """
    payload_json = OrderCreateModel(**payload.model_dump()).model_dump()
    service = OrdersApi(OrdersRepository())
    return service.create_order(payload_json)
    """

# ---------------------------------------------------------
#


@ROUTER.get('{/order_id}',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def get_order(order_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = read_order_processor.delay(order_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.get('',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def list_orders() -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = list_orders_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{order_id}/cancel",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def cancel_order(order_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = cancel_order_processor.delay(order_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{order_id}/validate",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def validate_order(order_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = validate_order_processor.delay(order_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{order_id}/reject",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def reject_order(order_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = reject_order_processor.delay(order_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
