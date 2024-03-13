# BUILTIN modules
from uuid import uuid4

# Third party modules
from pydantic import (BaseModel, UUID4, Field, EmailStr, ConfigDict)
from typing import List

# Local program modules
from ..database import PyObjectId


class EmployeeBase(BaseModel):
    """Base model for Employee data."""
    first_name: str
    last_name: str
    email: EmailStr


class EmployeeCreateModel(EmployeeBase):
    """Model for creating a new Employee."""
    pass


class EmployeeModel(EmployeeBase):
    """Model for representing a Employee."""
    id: PyObjectId

    class Config:
        """Configuration for the model."""
        allow_population_by_field_name = True


class EmployeesCollection(BaseModel):
    """Model for representing a collection of Employees."""
    Employees: List[EmployeeModel]


# -----------------------------------------------------------------------------
#
class NotFoundError(BaseModel):
    """ Define model for a http 404 exception (Not Found). """
    detail: str = "Employee not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Employee in DB"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
