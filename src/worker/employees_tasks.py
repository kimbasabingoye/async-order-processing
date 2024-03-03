# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-24 19:41:02
     $Rev: 41
"""

# BUILTIN modules
import json

# Third party modules

# Local modules
from ..config.setup import config
from .celery_app import response_handler, send_rabbit_response, send_restful_response, WORKER, logger
from ..api.employees.employee_api_adapter import EmployeesApi
from ..api.employees.employee_data_adapter import EmployeesRepository


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.create_employee',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_employee_processor(task: callable, payload: dict) -> dict:
    """ Create employee in DB

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = EmployeesApi(EmployeesRepository())

    return service.create_employee(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.read_employee',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_employee_processor(task: callable, employee_id: str) -> dict:
    """ Read employee in DB

    :param task: Current task.
    :param employee_id: employee id.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {employee_id}")

    service = EmployeesApi(EmployeesRepository())

    return service.get_employee(employee_id=employee_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_employees',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_employees_processor(task: callable) -> dict:
    """ List all employees in DB

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = EmployeesApi(EmployeesRepository())

    return service.list_employees()
