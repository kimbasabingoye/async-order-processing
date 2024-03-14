# BUILTIN modules
import json


# Local modules
from ..config.setup import config
from .celery_app import response_handler,  WORKER, logger
from ..api.quotations.quotation_api_adapter import QuotationsApi
from ..api.quotations.quotation_data_adapter import QuotationsRepository


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.create_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_quotation_processor(task: callable, payload: dict) -> dict:
    """ Create quotation in DB

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = QuotationsApi(QuotationsRepository())
    return service.create_quotation(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.read_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_quotation_processor(task: callable, quotation_id: str) -> dict:
    """ Read quotation in DB

    :param task: Current task.
    :param quotation_id: quotation id.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {quotation_id}")

    service = QuotationsApi(QuotationsRepository())

    return service.get_quotation(quotation_id=quotation_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_quotations',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_quotations_processor(task: callable) -> dict:
    """ List all quotations in DB

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = QuotationsApi(QuotationsRepository())

    return service.list_quotations()


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.cancel_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def cancel_quotation_processor(task: callable, quotation_id: str, author_id: str) -> dict:
    """ Cancel specified quotation in quotations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = QuotationsApi(QuotationsRepository())

    return service.cancel_quotation(quotation_id=quotation_id, author_id=author_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.validate_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def validate_quotation_processor(task: callable, quotation_id: str, author_id: str) -> dict:
    """ Validate specified quotation in quotations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = QuotationsApi(QuotationsRepository())

    return service.validate_quotation(quotation_id=quotation_id, author_id=author_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.reject_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def reject_quotation_processor(task: callable, quotation_id: int, author_id: str) -> dict:
    """ Refuse specified quotation in quotations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = QuotationsApi(QuotationsRepository())

    return service.reject_quotation(quotation_id=quotation_id, author_id=author_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.accept_quotation',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def accept_quotation_processor(task: callable, quotation_id: int, author_id: str) -> dict:
    """ Accept specified quotation in quotations collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = QuotationsApi(QuotationsRepository())

    return service.accept_quotation(quotation_id=quotation_id, author_id=author_id)
