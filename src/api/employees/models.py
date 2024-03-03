# BUILTIN modules
from uuid import uuid4

# Third party modules
from pydantic import (BaseModel, UUID4, Field, EmailStr, ConfigDict)
from typing import List

# Local program modules


# ---------------------------------------------------------
#
class EmployeeCreateModel(BaseModel):
    """ Representation of an data required when creating employee in the system. """
    first_name: str
    last_name: str
    email: EmailStr


# ---------------------------------------------------------
#
class EmployeeModel(EmployeeCreateModel):
    """ Representation of an Employee in the system. """
    id: UUID4 = Field(default_factory=uuid4)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)


class EmployeesCollection(BaseModel):
    """
    A container holding a list of `EmployeeModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    employees: List[EmployeeModel]


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
