# BUILTIN modules
import json

# Third party modules

# Local modules
from ..config.setup import config
from .celery_app import response_handler, WORKER, logger
from ..api.orders.order_api_adapter import OrdersAPIAdapter
from ..api.orders.order_data_adapter import OrdersRepository
from ..api.database import UpdateModel

MAX_TASK_RETRY = 0
# ---------------------------------------------------------
#


@WORKER.task(
    name='tasks.create_order',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def create_order_processor(task: callable, payload: dict) -> dict:
    """ Create order in DB

    :param task: Current task.
    :param payload: Process received message.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.create_order(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.read_order',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def read_order_processor(task: callable, order_id: str) -> dict:
    """ Read order in DB

    :param task: Current task.
    :param order_id: order id.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {order_id}")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.get_order(order_id=order_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_orders',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def list_orders_processor(task: callable) -> dict:
    """ List all orders in DB

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.list_orders()


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.list_order_quotations',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def list_order_quotations_processor(task: callable, order_id: str) -> dict:
    """ List quotations for specified order in DB

    :param task: Current task.
    :param order_id: Order id
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.list_order_quotations(order_id)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.cancel_order',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def cancel_order_processor(task: callable, payload: UpdateModel) -> dict:
    """ Cancel specified order in orders collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.cancel_order(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.validate_order',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def validate_order_processor(task: callable, payload: UpdateModel) -> dict:
    """ Validate specified order in orders collection

    :param task: Current task.
    :return: Processing response.
    """
    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.validate_order(payload)


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.reject_order',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=MAX_TASK_RETRY
)
def reject_order_processor(task: callable, payload: UpdateModel) -> dict:
    """ Reject specified order in orders collection

    :param task: Current task.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task.name}' is processing received payload: {payload}")

    service = OrdersAPIAdapter(OrdersRepository())

    return service.reject_order(payload)
