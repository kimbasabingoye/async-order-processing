import json

from loguru import logger

from ..config.setup import config
from .celery_app import response_handler, WORKER
from ..api.employees.employee_api_adapter import EmployeesAPIAdapter
from ..api.employees.employee_data_adapter import EmployeesRepository


def process_employee_task(task_name: str, payload: dict = None, employee_id: str = None) -> dict:
    """Process employee-related tasks."""
    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(
        f"Task '{task_name}' is processing received payload: {payload or employee_id}")

    service = EmployeesAPIAdapter(EmployeesRepository())

    if task_name == 'tasks.create_employee':
        return service.create_employee(payload)
    elif task_name == 'tasks.read_employee':
        return service.get_employee(employee_id=employee_id)
    elif task_name == 'tasks.list_employees':
        return service.list_employees()
    else:
        raise ValueError(f"Invalid task name: {task_name}")


@WORKER.task(
    name='tasks.create_employee',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def create_employee_processor(task: callable, payload: dict) -> dict:
    return process_employee_task(task.name, payload)


@WORKER.task(
    name='tasks.read_employee',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def read_employee_processor(task: callable, employee_id: str) -> dict:
    return process_employee_task(task.name, employee_id=employee_id)


@WORKER.task(
    name='tasks.list_employees',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def list_employees_processor(task: callable) -> dict:
    return process_employee_task(task.name)
