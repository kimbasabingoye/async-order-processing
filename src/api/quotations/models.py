# BUILTIN modules
from uuid import uuid4
from datetime import datetime
from enum import Enum

# Third party modules
from pydantic import (BaseModel, UUID4, Field,  EmailStr, ConfigDict)
from typing import List, Optional

# Local program modules
from ..database import PyObjectId


# ---------------------------------------------------------
#
class QuotationStatus(str, Enum):
    """ Quotation status changes.

    QGEN -> QVAL/QCAN -> QACC/QREJ
    """

    QUREV = 'quotationUnderReview'     
    QVAL = 'quotationValidated'     
    QCAN = 'quotationCancelled'       
    QREJ = 'quotationRejected'      
    QACC = 'quotationAccepted'      


# ---------------------------------------------------------
#
class QuotationCreateModel(BaseModel):
    """ Representation of an data required when creating order in the system. """
    price: int
    order_id: PyObjectId
    details: str
    owner_id: Optional[PyObjectId]  # generated or created by employee
    


# ---------------------------------------------------------
#
class StateUpdateSchema(BaseModel):
    """ Representation of an Quotation status history in the system. """
    new_status: QuotationStatus
    when: datetime = Field(default_factory=datetime.utcnow)
    # is_employee: bool
    by: PyObjectId

    def dict(self):
        return {
            'new_status': self.new_status,
            'when': self.when.isoformat(),
            'by': self.by
        }


class QuotationCreateInternalModel(QuotationCreateModel):
    """ Representation of an data required when creating order in the system. """
    status: QuotationStatus
    update_history: Optional[List[StateUpdateSchema]]
    created: datetime = Field(default_factory=datetime.utcnow)
    


class QuotationModel(QuotationCreateInternalModel):
    """ Representation of Quotation in the system. """

    id: PyObjectId = Field(alias="_id", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)

    # ---------------------------------------------------------
    #

    def dict(self) -> dict:
        """Return dictionary representation of QuotationModel."""
        data = {
            'id': str(self.id),
            'order_id': self.order_id,
            'owner_id': self.owner_id,
            'price': self.price,
            'status': self.status,
            'created': self.created.isoformat(),
            'details': self.details
        }
        # Handle the case where update_history might be None
        if self.update_history is not None:
            # Iterate over each item in update_history and call its dict method
            data['update_history'] = [update.dict()
                                      for update in self.update_history]
        return data


# -----------------------------------------------------------------------------
#
class NotFoundError(BaseModel):
    """ Define model for a http 404 exception (Not Found). """
    detail: str = "Quotation not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Quotation in DB"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
