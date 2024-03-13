# BUILTIN modules
from uuid import uuid4

# Third party modules
from pydantic import (BaseModel, UUID4, Field, EmailStr, ConfigDict)
from typing import List

# Local program modules
from ..database import PyObjectId

# ---------------------------------------------------------
#
class CustomerCreateModel(BaseModel):
    """ Representation of an data required when creating customer in the system. """
    first_name: str
    last_name: str
    email: EmailStr


# ---------------------------------------------------------
#
class CustomerModel(CustomerCreateModel):
    """ Representation of an Customer in the system. """
    id: PyObjectId

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)


class CustomersCollection(BaseModel):
    """
    A container holding a list of `CustomerModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    customers: List[CustomerModel]


# -----------------------------------------------------------------------------
#
class NotFoundError(BaseModel):
    """ Define model for a http 404 exception (Not Found). """
    detail: str = "Customer not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Customer in DB"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
