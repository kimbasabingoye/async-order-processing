# BUILTIN modules
from uuid import uuid4

# Third party modules
from pydantic import (BaseModel, UUID4, Field, EmailStr, ConfigDict)
from typing import List

# Local program modules
from ..database import PyObjectId


class CustomerBase(BaseModel):
    """Base model for customer data."""
    first_name: str
    last_name: str
    email: EmailStr


class CustomerCreateModel(CustomerBase):
    """Model for creating a new customer."""
    pass


class CustomerModel(CustomerBase):
    """Model for representing a customer."""
    id: PyObjectId

    class Config:
        """Configuration for the model."""
        allow_population_by_field_name = True


class CustomersCollection(BaseModel):
    """Model for representing a collection of customers."""
    customers: List[CustomerModel]



# -----------------------------------------------------------------------------
#
class NotFoundError(BaseModel):
    """ Define model for a http 404 exception (Not Found). """
    detail: str = "Customer not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Customer in DB"

