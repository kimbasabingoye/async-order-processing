
# Third party modules
from fastapi import HTTPException
from bson import ObjectId
from pydantic import UUID4
from typing import List

# Local modules
from .models import EmployeeCreateModel, EmployeeModel, EmployeesCollection
from ..database import db, from_mongo


class EmployeesRepository:
    """ This class implements the data layer adapter (the CRUD operations).
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    def _read(employee_id: UUID4) -> EmployeeModel:
        """ Read Employee for matching index key from DB collection employees.

        :param key: Index key.
        :return: Found Employee.
        """

        response = db.employees.find_one({"_id": ObjectId(employee_id)})

        return from_mongo(response)
    
    # ---------------------------------------------------------
    #
    def check_employee(self, employee_id: str) -> bool:
        """ Check if the customer exist.

        :param key: Index key.
        :return: True if customer is found and False if not.
        """

        response = self._read(employee_id)

        if response:
            return True

        return False

    # ---------------------------------------------------------
    #

    def read(self, employee_id: str) -> EmployeeModel:
        """ Read Employee for matching index key from DB collection employees.

        :param key: Index key.
        :return: Found Employee.
        """

        response = self._read(employee_id=employee_id)

        return response

    # ---------------------------------------------------------
    #

    def create(self, payload: EmployeeCreateModel) -> str:
        """ Create Employee in employees collections.

        :param payload: New employee payload.
        :return: Created employee.
        """
        try:
            new_employee = db.employees.insert_one(payload)
            # created_employee = self.read(str(new_employee.inserted_id))
            return str(new_employee.inserted_id)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500,
                                detail=f"Employee creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[EmployeeModel]:
        """ Read Employee in employee collection.

        :return: list of found employees.
        """

        employees = db.employees.find({})

        return list(map(from_mongo, employees))
