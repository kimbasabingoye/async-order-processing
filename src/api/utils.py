from ..api.employees.employee_data_adapter import EmployeesRepository
from ..api.customers.customer_data_adapter import CustomersRepository
from ..api.orders.order_data_adapter import OrdersRepository
from fastapi import HTTPException, status


def validate_user_is_employee(user_id) -> None:
    """Check if the author is an employee."""
    if not EmployeesRepository().check_exists(user_id):
        raise HTTPException(
            status_code=403, detail=f"Operation not allowed. You must be an employee.")
    

def validate_user_is_customer(user_id) -> None:
    """Check if the author is a customer."""
    if not CustomersRepository().check_exists(user_id):
        raise HTTPException(
            status_code=403, detail=f"Operation not allowed. You must be a customer.")

def validate_order_exist(order_id) -> None:
    """Check if the order exist."""
    if not OrdersRepository().check_exists(order_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object not found: {order_id}")
