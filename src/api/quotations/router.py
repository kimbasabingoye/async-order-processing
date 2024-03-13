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
from .quotation_api_adapter import QuotationsApi
# from .documentation import quotation_id_documentation
from .quotation_data_adapter import QuotationsRepository
from .models import (QuotationCreateModel, QuotationModel,
                     NotFoundError, FailedUpdateError, ConnectError)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.quotations_tasks import create_quotation_processor, read_quotation_processor, list_quotations_processor, accept_quotation_processor, reject_quotation_processor, validate_quotation_processor, cancel_quotation_processor

# Constants
ROUTER = APIRouter(prefix=f"/v1/quotations", tags=[f"Quotations"])
""" Quotation API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post('',
             status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
def create_quotation(payload: QuotationCreateModel) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    # payload_json = QuotationCreateModel(**payload.model_dump()).model_dump()
    payload_json = payload.model_dump()
    #print(payload_json)
    try:
        # Add payload message to Celery for processing.
        result = create_quotation_processor.delay(payload_json)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
    """
    payload_json = QuotationCreateModel(**payload.model_dump()).model_dump()
    service = QuotationsApi(QuotationsRepository())
    return service.create_quotation(payload_json)
    """

# ---------------------------------------------------------
#


@ROUTER.get('{/quotation_id}',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def get_quotation(quotation_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = read_quotation_processor.delay(quotation_id)
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
async def list_quotations() -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = list_quotations_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)



# ---------------------------------------------------------
#
@ROUTER.post(
    "/{quotation_id}/cancel",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def cancel_quotation(quotation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = cancel_quotation_processor.delay(quotation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{quotation_id}/validate",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def validate_quotation(quotation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = validate_quotation_processor.delay(quotation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{quotation_id}/reject",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def reject_quotation(quotation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = reject_quotation_processor.delay(quotation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{quotation_id}/accept",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def accept_quotation(quotation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = accept_quotation_processor.delay(quotation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
