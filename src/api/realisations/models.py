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
class RealisationStatus(str, Enum):
    """ Realisation status changes.

    RSCH -> RSTA -> RFIN
    """

    RSCH = 'realisationScheduled'     # RealisationService
    RSTA = 'realisationStarted'         # RealisationService
    RCOM = 'realisationCompleted'       # RealisationService
    

# ---------------------------------------------------------
#
class RealisationCreateModel(BaseModel):
    """ Representation of an data required when creating order in the system. """
    order_id: PyObjectId
    employee_id: PyObjectId
    created_by: Optional[PyObjectId]  # generated or created by employee
    


# ---------------------------------------------------------
#
class StateUpdateSchema(BaseModel):
    """ Representation of an Realisation status history in the system. """
    new_status: RealisationStatus
    when: datetime = Field(default_factory=datetime.utcnow)
    # is_employee: bool
    by: PyObjectId
    comment: str = ""

    def dict(self):
        return {
            'new_status': self.new_status,
            'when': self.when.isoformat(),
            'by': self.by,
            'comment': self.comment
        }


class RealisationCreateInternalModel(RealisationCreateModel):
    """ Representation of an data required when creating order in the system. """
    status: RealisationStatus
    assignment_date: datetime = Field(default_factory=datetime.utcnow)
    update_history: Optional[List[StateUpdateSchema]]


class RealisationModel(RealisationCreateInternalModel):
    """ Representation of Realisation in the system. """

    id: PyObjectId = Field(alias="_id", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)

    # ---------------------------------------------------------
    #

    def dict(self) -> dict:
        """Return dictionary representation of RealisationModel."""
        data = {
            'id': str(self.id),
            'order_id': self.order_id,
            'employee_id': self.employee_id,
            'created_by': self.created_by,
            'status': self.status,
            'assignment_date': self.assignment_date.isoformat()
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
    detail: str = "Realisation not found in DB"


class FailedUpdateError(BaseModel):
    """ Define model for a http 400 exception (Unprocessable Entity). """
    detail: str = "Failed updating Realisation in DB"


class ConnectError(BaseModel):
    """ Define model for a http 500 exception (INTERNAL_SERVER_ERROR). """
    detail: str = "Failed to connect to internal MicroService"
