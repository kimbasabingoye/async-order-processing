import json

from loguru import logger

from ..config.setup import config
from .celery_app import response_handler, send_rabbit_response, send_restful_response, WORKER
from ..api.customers.customer_api_adapter import CustomersAPIAdapter
from ..api.customers.customer_data_adapter import CustomersRepository


def process_customer_task(task_name: str, payload: dict = None, customer_id: str = None) -> dict:
    """Process customer-related tasks."""
    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task_name}' is processing received payload: {payload or customer_id}")

    service = CustomersAPIAdapter(CustomersRepository())

    if task_name == 'tasks.create_customer':
        return service.create_customer(payload)
    elif task_name == 'tasks.read_customer':
        return service.get_customer(customer_id=customer_id)
    elif task_name == 'tasks.list_customers':
        return service.list_customers()
    else:
        raise ValueError(f"Invalid task name: {task_name}")


@WORKER.task(
    name='tasks.create_customer',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_customer_processor(task: callable, payload: dict) -> dict:
    return process_customer_task(task.name, payload)


@WORKER.task(
    name='tasks.read_customer',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_customer_processor(task: callable, customer_id: str) -> dict:
    return process_customer_task(task.name, customer_id=customer_id)


@WORKER.task(
    name='tasks.list_customers',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_customers_processor(task: callable) -> dict:
    return process_customer_task(task.name)
