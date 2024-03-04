# BUILTIN modules
from uuid import uuid4
from datetime import datetime
from enum import Enum

# Third party modules
from pydantic import (BaseModel, UUID4, Field,  EmailStr, ConfigDict)
from typing import List, Optional

# Local program modules
from ..database import PyObjectId


class Services(str, Enum):
    """ Representation of valid services in the system. """
    web_site = 'Make a web site'
    mobile_app = 'Make a mobile app'
    desktop_app = 'Make a desktop app'


# ---------------------------------------------------------
#
class OrderStatus(str, Enum):
    """ Order status changes.

    CREA -> ORAC/OREJ/ORCA -> QGEN -> QVAL/QREJ -> RESC -> DONE

    """
    UREV = 'underReview'            # OrderService
    ORAC = 'orderAccepted'          # OrderService
    OREJ = 'orderRejected'          # OrderService
    ORCA = 'orderCancelled'         # OrderService
    RESC = 'realisationScheduled'   # OrderService
    DONE = 'delivered'              # OrderService

    """
    QGEN = 'quotationGenerated'     # QuotationService
    QVAL = 'quotationValidated'     # QuotationService
    QREJ = 'quotationRejected'      # QuotationService
    """


# ---------------------------------------------------------
#
class OrderCreateModel(BaseModel):
    """ Representation of an data required when creating order in the system. """
    customer_id: PyObjectId
    service: Services
    description: str

# ---------------------------------------------------------
#


class StateUpdateSchema(BaseModel):
    """ Representation of an Order status history in the system. """
    new_status: OrderStatus
    when: datetime = Field(default_factory=datetime.utcnow)
    #is_employee: bool
    by: PyObjectId

    def dict(self):
        return {
            'new_status': self.new_status,
            'when': self.when.isoformat(),
            #'is_employee': self.is_employee,
            'by': self.by
        }


class OrderCreateInternalModel(OrderCreateModel):
    """ Representation of an data required when creating order in the system. """
    status: OrderStatus
    update_history: Optional[List[StateUpdateSchema]]
    created: datetime = Field(default_factory=datetime.utcnow)


class OrderModel(OrderCreateInternalModel):
    """ Representation of Order in the system. """

    id: PyObjectId = Field(alias="_id", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)

    # ---------------------------------------------------------
    #

    def dict(self) -> dict:
        """Return dictionary representation of OrderModel."""
        data = {
            'id': str(self.id),
            'service': self.service,
            'description': self.description,
            'status': self.status,
            'created': self.created.isoformat(),
            'customer_id': str(self.customer_id)
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
    detail: str = "Order not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Order in DB"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
