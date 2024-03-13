from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from .employee_data_adapter import EmployeesRepository
from .models import EmployeeModel, EmployeeCreateModel
from ..base_api_adapter import BaseAPIAdapter


class EmployeesAPIAdapter(BaseAPIAdapter):
    """
    API adapter for handling customer-related operations.
    """

    def __init__(self, repository: EmployeesRepository):
        super().__init__(repository)

    def get_customer(self, customer_id: str) -> EmployeeModel:
        """Get a customer by ID."""
        return self.get_obj(customer_id)

    def create_customer(self, payload: EmployeeCreateModel) -> EmployeeModel:
        """Create a new customer."""
        return self.create_obj(payload)

    def list_customers(self) -> List[EmployeeModel]:
        """List all customers."""
        return self.read_all_obj()
