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
from .order_api_adapter import OrdersAPIAdapter
# from .documentation import order_id_documentation
from .order_data_adapter import OrdersRepository
from .models import (OrderCreateModel,
                     NotFoundError, FailedUpdateError, ConnectError)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.orders_tasks import create_order_processor, read_order_processor, list_orders_processor, cancel_order_processor, validate_order_processor, reject_order_processor, list_order_quotations_processor
from ..database import UpdateModel

router = APIRouter(prefix="/v1/orders", tags=["Orders"])
adapter = OrdersAPIAdapter(OrdersRepository())


# ---------------------------------------------------------
#
@router.post(
    '',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ProcessResponseModel,
    responses={
        500: {"model": UnknownError}
    },
    dependencies=[Depends(validate_authentication)]
)
async def create_order(payload: OrderCreateModel) -> ProcessResponseModel:
    try:
        result = create_order_processor.delay(payload.model_dump())
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


@router.get(
    '/{order_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ProcessResponseModel,
    responses={500: {"model": UnknownError}},
    dependencies=[Depends(validate_authentication)]
)
async def get_order(order_id: str) -> ProcessResponseModel:
    try:
        result = read_order_processor.delay(order_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


@router.get('/{order_id}/quotations',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def list_order_quotations(order_id: str) -> ProcessResponseModel:
    try:
        result = list_order_quotations_processor.delay(order_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@router.get('',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def list_orders() -> ProcessResponseModel:
    try:
        result = list_orders_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@router.post(
    "/{order_id}/cancel",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def cancel_order(payload: UpdateModel) -> ProcessResponseModel:
    try:
        result = cancel_order_processor.delay(payload.model_dump())
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@router.post(
    "/{order_id}/validate",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def validate_order(payload: UpdateModel)-> ProcessResponseModel:
    try:
        result = validate_order_processor.delay(payload.model_dump())
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@router.post(
    "/{order_id}/reject",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def reject_order(payload: UpdateModel) -> ProcessResponseModel:
    try:
        result = reject_order_processor.delay(payload.model_dump())
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
