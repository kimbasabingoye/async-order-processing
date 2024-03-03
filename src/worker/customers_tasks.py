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
from ..api.customers.customer_api_adapter import CustomersApi
from ..api.customers.customer_data_adapter import CustomersRepository


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.create_customer',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_customer_processor(task: callable, payload: dict) -> dict:
    """ Create customer in DB

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = CustomersApi(CustomersRepository())

    return service.create_customer(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.read_customer',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_customer_processor(task: callable, customer_id: str) -> dict:
    """ Read customer in DB

    :param task: Current task.
    :param customer_id: customer id.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {customer_id}")

    service = CustomersApi(CustomersRepository())

    return service.get_customer(customer_id=customer_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_customers',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_customers_processor(task: callable) -> dict:
    """ List all customers in DB

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = CustomersApi(CustomersRepository())

    return service.list_customers()
