from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from .employee_data_adapter import EmployeesRepository
from .models import EmployeeModel, EmployeeCreateModel
from ..base_api_adapter import BaseAPIAdapter


class EmployeesAPIAdapter(BaseAPIAdapter):
    """
    API adapter for handling employee-related operations.
    """

    def __init__(self, repository: EmployeesRepository):
        super().__init__(repository)

    def get_employee(self, employee_id: str) -> EmployeeModel:
        """Get a employee by ID."""
        return self.get_obj(employee_id)

    def create_employee(self, payload: EmployeeCreateModel) -> EmployeeModel:
        """Create a new employee."""
        return self.create_obj(payload)

    def list_employees(self) -> List[EmployeeModel]:
        """List all employees."""
        return self.read_all_obj()
