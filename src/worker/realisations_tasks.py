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
from ..api.realisations.realisation_api_adapter import RealisationsApi
from ..api.realisations.realisation_data_adapter import RealisationsRepository


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.create_realisation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_realisation_processor(task: callable, payload: dict) -> dict:
    """ Create realisation in DB

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = RealisationsApi(RealisationsRepository())
    return service.create_realisation(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.read_realisation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_realisation_processor(task: callable, realisation_id: str) -> dict:
    """ Read realisation in DB

    :param task: Current task.
    :param realisation_id: realisation id.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {realisation_id}")

    service = RealisationsApi(RealisationsRepository())

    return service.get_realisation(realisation_id=realisation_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_realisations',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_realisations_processor(task: callable) -> dict:
    """ List all realisations in DB

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = RealisationsApi(RealisationsRepository())

    return service.list_realisations()




# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.complete_realisation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def complete_realisation_processor(task: callable, realisation_id: str, author_id: str) -> dict:
    """ Complete specified realisation in realisations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = RealisationsApi(RealisationsRepository())

    return service.complete_realisation(realisation_id=realisation_id, author_id=author_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.start_realisation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def start_realisation_processor(task: callable, realisation_id: int, author_id: str) -> dict:
    """ Start specified realisation in realisations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = RealisationsApi(RealisationsRepository())

    return service.start_realisation(realisation_id=realisation_id, author_id=author_id)
