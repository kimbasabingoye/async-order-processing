
from datetime import datetime
import json

# Third party modules
from fastapi import HTTPException
from pydantic import UUID4

# Local modules
from .employee_data_adapter import EmployeesRepository
from .models import EmployeesCollection, EmployeeCreateModel, EmployeeModel


# ------------------------------------------------------------------------
#
class EmployeesApi:
    """
    This class implemnts the Web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: EmployeesRepository):
        """ The class initializer.

        :param repository: Data layer handler object
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    def _employee_of(self, employee_id: UUID4) -> EmployeeModel:
        """ Return specified employee.

        :param employee_id: employee id for employee to find.
        :return: Found employee object.
        :raise HTTPException [404]: when employee not found in DB.
        """
        db_employee = self.repo.read(employee_id)

        if not db_employee:
            errmsg = f"{employee_id} not found in DB api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_employee

    # ---------------------------------------------------------
    #

    def get_employee(self, employee_id: str) -> EmployeeModel:
        """ Return specified employee. 

        :param employee_id: employee id for employee to find.
        :return: Found employee object.
        :raise HTTPException [404]: when employee not found in DB api_db.employees.
        """
        db_employee = self._employee_of(employee_id)

        return db_employee

    # ---------------------------------------------------------
    #

    def create_employee(self, payload: EmployeeCreateModel) -> EmployeeModel:
        """ Create a new employee in DB.

        :param payload: employee payload.
        :return: Created employee object.
        :raise HTTPException [400]: when create employee in DB api_db.employees failed.
        """

        return self.repo.create(payload=payload)

    # ---------------------------------------------------------
    #

    def list_employees(self) -> EmployeesCollection:
        """ list all existing employees in DB api_db.employees.

        :return: list of found employees
        """

        db_employees = self.repo.read_all()

        return db_employees
