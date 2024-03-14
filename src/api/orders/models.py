# BUILTIN modules
from uuid import uuid4
from datetime import datetime
from enum import Enum

# Third party modules
from pydantic import (BaseModel, Field, ConfigDict)
from typing import List, Optional

# Local program modules
from src.api.database import PyObjectId, StateUpdateSchema
from .services import Services


class OrderStatus(str, Enum):
    """ Order status changes.

    UREV -> ORAC/OREJ/ORCA -> RESC -> REST -> RECO

    """
    UREV = 'underReview'
    ORAC = 'orderAccepted'
    OREJ = 'orderRejected'
    ORCA = 'orderCancelled'
    RESC = 'realisationScheduled'
    REST = 'realisationStarted'
    RECO = 'realisationCompleted'


class OrderCreateModel(BaseModel):
    """ Representation of data required when creating an order in the system. """
    customer_id: PyObjectId
    service: Services
    description: str


class OrderCreateInternalModel(BaseModel):
    """ Representation of data required when creating an order in the system. """
    customer_id: PyObjectId
    service: Services
    description: str
    status: OrderStatus
    update_history: Optional[List[StateUpdateSchema]]
    created: datetime = Field(default_factory=datetime.utcnow)



class OrderModel(BaseModel):
    """ Representation of an order in the system. """
    id: PyObjectId = Field(alias="_id", default=None)
    customer_id: PyObjectId
    service: Services
    description: str
    status: OrderStatus
    update_history: Optional[List[StateUpdateSchema]]
    created: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)

    def to_dict(self) -> dict:
        """Converts OrderModel instance to dictionary."""
        data = {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'service': self.service,
            'description': self.description,
            'status': self.status.value,
            'created': self.created.isoformat(),
        }
        if self.update_history:
            data['update_history'] = [update.dict()
                                      for update in self.update_history]
        return data


class NotFoundError(BaseModel):
    """ Model for a 404 exception (Not Found). """
    detail: str = "Order not found in DB"


class FailedUpdateError(BaseModel):
    """ Model for a 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Order in DB"


class ConnectError(BaseModel):
    """ Model for a 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
