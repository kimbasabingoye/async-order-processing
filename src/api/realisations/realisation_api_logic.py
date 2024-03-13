# BUILTIN modules
from datetime import datetime
from typing import Optional, List

# Third party modules
from fastapi import HTTPException

# Local modules
from .models import RealisationStatus, RealisationModel, RealisationCreateModel, StateUpdateSchema, RealisationCreateInternalModel
from .realisation_data_adapter import RealisationsRepository
from ..orders.order_data_adapter import OrdersRepository
from ..orders.models import OrderStatus
from ..quotations.quotation_data_adapter import QuotationsRepository
from ..employees.employee_data_adapter import EmployeesRepository


# ------------------------------------------------------------------------
#
class RealisationApiLogic:
    """
    This class implements the Realisation web API business logic layer.
    """

    # ---------------------------------------------------------
    #
    def __init__(
            self,
            repository: RealisationsRepository,
            employee_id: str,
            order_id: str,
            id: str = None,
            status: RealisationStatus = None,
            assignment_date: datetime = None,
            created_by: str = None,
            update_history: List[StateUpdateSchema] = None,
            author_id: int = None,  # for realisation modification
            # new_status: RealisationStatus = None  # for realisation modification
    ):
        """ The class initializer.

        :param id: Realisation id.
        :param customer_id: The individual that assignment_date the realisation.
        :param status: Current realisation status.
        :param assignment_date: Realisation assignment_date timestamp.


        """
        self.id = id
        self.order_id = order_id
        self.employee_id = employee_id
        self.status = status
        self.assignment_date = assignment_date
        self.update_history = update_history
        self.author_id = author_id
        self.created_by = created_by

        # Initialize objects.
        self.repo = repository

    # ---------------------------------------------------------
    #
    def create(self) -> RealisationModel:
        """ Create a new realisation in DB.

        - check if the customer exist(registred) in customer collection
        - Then create the realisation if the customer is registred

        :raise HTTPException [400]: when create realisation in realisations table failed.
        """

        # Check the existence of the order
        order_repo = OrdersRepository()
        order_exist = order_repo.check_order(self.order_id)
        if not order_exist:
            errmsg = f"Operation not allowed. Order: {self.order_id} don't exist"
            raise HTTPException(status_code=403, detail=errmsg)

        # Check if the order status is validated
        order_validated = order_repo.is_validated(self.order_id)
        if not order_validated:
            errmsg = f"Operation not allowed. Order {self.order_id} status is {order_repo.get_status(self.order_id)}"
            raise HTTPException(status_code=403, detail=errmsg)
        
        # Check if there is a accepted quotation for this order
        quotation_repo = QuotationsRepository()
        accepted_quotation_exist = quotation_repo.have_accepted_quotation(self.order_id)
        if not accepted_quotation_exist:
            errmsg = f"Operation not allowed. Order: {self.order_id} don't have accepted quotation"
            raise HTTPException(status_code=403, detail=errmsg)
        
        # if the author is set i.e this realisation is created manually
        # check if the author is an employee
        if self.created_by is not None:
            employee_exist = EmployeesRepository().check_employee(self.created_by)

            if not employee_exist:
                errmsg = f"You are not allowed to perform this operation."
                raise HTTPException(status_code=403, detail=errmsg)


        # Create a new Realisation in DB.
        db_realisation = RealisationCreateInternalModel(
            order_id=self.order_id,
            employee_id=self.employee_id,
            created_by=self.created_by,
            status=RealisationStatus.RSCH,
            assignment_date=datetime.utcnow(),
            update_history=[])

        new_realisation_id = self.repo.create(db_realisation)

        if not new_realisation_id:
            errmsg = f"Create failed for {self.id=} in realisations collection"
            raise HTTPException(status_code=400, detail=errmsg)
        
        # Update order status to RSCH
        response = order_repo.update(
            order_id=self.order_id, new_status=OrderStatus.RESC, author_id=self.author_id)
        
        if not response: # update failed
            errmsg = f"Order status update failed"
            raise HTTPException(status_code=400, detail=errmsg)

    
        return new_realisation_id


    # ---------------------------------------------------------
    #
    def start(self) -> bool:
        """ Start current realisation.

        :raise HTTPException [403]: when start request came too late.
        :raise HTTPException [400]: when Realisation update in realisations table failed.
        """

        if self.status != RealisationStatus.RSCH:
            errmsg = f'Could not start realisation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        
        # check the author right
        # check if the author is an employee
        if self.author_id is None:
            errmsg = f"Missing author id."
            raise HTTPException(status_code=403, detail=errmsg)
            
        employee_exist = EmployeesRepository().check_employee(self.author_id)
        if not employee_exist:
                errmsg = f"You are not allowed to perform this operation."
                raise HTTPException(status_code=403, detail=errmsg)
        
        # check if the author is the owner of the realiation
        if self.author_id != self.employee_id:
            errmsg = f"Operation not allowed. You must be the owner of the realisation"
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Realisation status in DB.
        started_realisation = self.repo.update(
            realisation_id=self.id, new_status=RealisationStatus.RSTA, author_id=self.author_id)

        if not started_realisation:
            errmsg = f"Failed updating {self.id=} in realisations table"
            raise HTTPException(status_code=400, detail=errmsg)

        # Update order status to REST
        order_repo = OrdersRepository()
        response = order_repo.update(
            order_id=self.order_id, new_status=OrderStatus.REST, author_id=self.author_id)
        
        if not response:  # update failed
            errmsg = f"Order status update failed"
            raise HTTPException(status_code=400, detail=errmsg)

        return True

    # ---------------------------------------------------------
    #
    def complete(self) -> bool:
        """ Complete current realisation.

        :raise HTTPException [403]: when complete request came too late.
        :raise HTTPException [400]: when Realisation update in realisations table failed.
        """

        if self.status != RealisationStatus.RSTA:
            errmsg = f'Could not complete realisation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # check the author right
        # check if the author is an employee
        if self.author_id is None:
            errmsg = f"Missing author id."
            raise HTTPException(status_code=403, detail=errmsg)

        employee_exist = EmployeesRepository().check_employee(self.author_id)
        if not employee_exist:
            errmsg = f"You are not allowed to perform this operation."
            raise HTTPException(status_code=403, detail=errmsg)

        # check if the author is the owner of the realiation
        if self.author_id != self.employee_id:
            errmsg = f"Operation not allowed. You must be the owner of the realisation"
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Realisation status in DB.
        started_realisation = self.repo.update(
            realisation_id=self.id, new_status=RealisationStatus.RCOM, author_id=self.author_id)

        if not started_realisation:
            errmsg = f"Failed updating {self.id=} in realisations table"
            raise HTTPException(status_code=400, detail=errmsg)

        # Update order status to REST
        order_repo = OrdersRepository()
        response = order_repo.update(
            order_id=self.order_id, new_status=OrderStatus.RECO, author_id=self.author_id)

        if not response:  # update failed
            errmsg = f"Order status update failed"
            raise HTTPException(status_code=400, detail=errmsg)

        return True
