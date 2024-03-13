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
from .realisation_api_adapter import RealisationsApi
# from .documentation import realisation_id_documentation
from .realisation_data_adapter import RealisationsRepository
from .models import (RealisationCreateModel, RealisationModel,
                     NotFoundError, FailedUpdateError, ConnectError)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.realisations_tasks import create_realisation_processor, read_realisation_processor, list_realisations_processor, start_realisation_processor, complete_realisation_processor

# Constants
ROUTER = APIRouter(prefix=f"/v1/realisations", tags=[f"Realisations"])
""" Realisation API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post('',
             status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
def create_realisation(payload: RealisationCreateModel) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    # payload_json = RealisationCreateModel(**payload.model_dump()).model_dump()
    payload_json = payload.model_dump()
    #print(payload_json)
    try:
        # Add payload message to Celery for processing.
        result = create_realisation_processor.delay(payload_json)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)

# ---------------------------------------------------------
#


@ROUTER.get('{/realisation_id}',
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def get_realisation(realisation_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = read_realisation_processor.delay(realisation_id)
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
async def list_realisations() -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = list_realisations_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{realisation_id}/start",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def start_realisation(realisation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = start_realisation_processor.delay(realisation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    "/{realisation_id}/complete",
    response_model=ProcessResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        500: {'model': ConnectError},
        404: {'model': NotFoundError},
        400: {'model': FailedUpdateError}
    },
    dependencies=[Depends(validate_authentication)])
async def complete_realisation(realisation_id: str, author_id: str) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""
    try:
        # Add payload message to Celery for processing.
        result = complete_realisation_processor.delay(realisation_id, author_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
