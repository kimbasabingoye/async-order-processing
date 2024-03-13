# -*- coding: utf-8 -*-

from typing import List

from fastapi import APIRouter, HTTPException, Depends
from kombu.exceptions import OperationalError
from loguru import logger

from .models import CustomerCreateModel
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.customers_tasks import create_customer_processor, read_customer_processor, list_customers_processor


# Create API router
router = APIRouter(prefix="/v1/customers", tags=["Customers"])


# Endpoint for creating a customer
@router.post(
    "",
    status_code=202,
    response_model=ProcessResponseModel,
    responses={500: {"model": UnknownError}},
    dependencies=[Depends(validate_authentication)]
)
async def create_customer(payload: CustomerCreateModel) -> ProcessResponseModel:
    try:
        # Trigger Celery task processing of the payload
        result = create_customer_processor.delay(payload.model_dump())
        logger.debug(f"Added task [{result.id}] to Celery for processing")
        return ProcessResponseModel(status=result.state, id=result.id)
    except OperationalError as e:
        errmsg = f"Celery task initialization failed: {e}"
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# Endpoint for retrieving a customer
@router.get(
    "{/customer_id}",
    status_code=202,
    response_model=ProcessResponseModel,
    responses={500: {"model": UnknownError}},
    dependencies=[Depends(validate_authentication)]
)
async def get_customer(customer_id: str) -> ProcessResponseModel:
    try:
        # Trigger Celery task processing to retrieve the customer
        result = read_customer_processor.delay(customer_id)
        logger.debug(f"Added task [{result.id}] to Celery for processing")
        return ProcessResponseModel(status=result.state, id=result.id)
    except OperationalError as e:
        errmsg = f"Celery task initialization failed: {e}"
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)



# Endpoint for listing all customers
@router.get(
    "",
    status_code=202,
    response_model=ProcessResponseModel,
    responses={500: {"model": UnknownError}},
    dependencies=[Depends(validate_authentication)]
)
async def list_customers() -> ProcessResponseModel:
    try:
        # Trigger Celery task processing to list all customers
        result = list_customers_processor.delay()
        logger.debug(f"Added task [{result.id}] to Celery for processing")
        return ProcessResponseModel(status=result.state, id=result.id)
    except OperationalError as e:
        errmsg = f"Celery task initialization failed: {e}"
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
