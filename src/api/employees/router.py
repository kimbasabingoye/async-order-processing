from fastapi import HTTPException, Depends, APIRouter
from kombu.exceptions import OperationalError
from loguru import logger

from .models import (EmployeeCreateModel)
from ..models import ProcessResponseModel, UnknownError
from ...tools.security import validate_authentication
from ...worker.employees_tasks import create_employee_processor, read_employee_processor, list_employees_processor

# Constants
ROUTER = APIRouter(prefix=f"/v1/employees", tags=[f"Employees"])
""" Employee API endpoint router. """


@ROUTER.post("",
             status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
async def create_employee(payload: EmployeeCreateModel) -> ProcessResponseModel:
    payload_json = EmployeeCreateModel(**payload.model_dump()).model_dump()
    try:
        # Add payload message to Celery for processing.
        result = create_employee_processor.delay(payload_json)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


@ROUTER.get(
        "/{employee_id}",
        status_code=202,
        response_model=ProcessResponseModel,
        responses={500: {"model": UnknownError}},
        dependencies=[Depends(validate_authentication)])
async def get_employee(employee_id: str) -> ProcessResponseModel:
    try:
        result = read_employee_processor.delay(employee_id)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)
    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


@ROUTER.get("",
            status_code=202,
            response_model=ProcessResponseModel,
            responses={500: {"model": UnknownError}},
            dependencies=[Depends(validate_authentication)])
async def list_employees() -> ProcessResponseModel:
    try:
        result = list_employees_processor.delay()
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)
