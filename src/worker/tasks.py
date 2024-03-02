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
import time
import random

# Third party modules

# Local modules
from ..config.setup import config
from .celery_app import response_handler, send_rabbit_response, send_restful_response, WORKER, logger


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.processor',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def processor(task: callable, payload: dict) -> dict:
    """ Let's simulate a long-running task here.

    Using the random module to generate errors now and
    then to be able to test the retry functionality.

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    # Mimic random error for testing purposes.
    if not random.choice([0, 1]):
        raise ValueError('Oops, something went wrong')

    # Simulate a lengthy processing task.
    time.sleep(15)

    # Return the processing result of the lengthy task.
    return {'message': 'Lots of work was done here'}
