# BUILTIN modules
from datetime import datetime
from typing import Optional, List
import random


# Third party modules
from fastapi import HTTPException

# Local modules
from .models import QuotationStatus, QuotationModel, QuotationCreateModel, StateUpdateSchema, QuotationCreateInternalModel
from .quotation_data_adapter import QuotationsRepository
from ..orders.order_data_adapter import OrdersRepository
from ..orders.models import OrderStatus
from ..employees.employee_data_adapter import EmployeesRepository
from ..customers.customer_data_adapter import CustomersRepository
from ..realisations.realisation_data_adapter import RealisationsRepository
from ..realisations.realisation_api_adapter import RealisationsApi
from ..realisations.models import RealisationCreateModel

from ...tools.custom_logging import create_unified_logger

logger = create_unified_logger()


# ------------------------------------------------------------------------
#
class QuotationApiLogic:
    """
    This class implements the Quotation web API business logic layer.
    """

    # ---------------------------------------------------------
    #
    def __init__(
            self,
            repository: QuotationsRepository,
            price: int,
            order_id: str,
            owner_id: str = None,  # generated or employee
            details: str = None,
            id: int = None,
            status: QuotationStatus = None,
            created: datetime = None,
            update_history: List[StateUpdateSchema] = None,
            updater_id: int = None,  # for quotation modification
            # new_status: QuotationStatus = None  # for quotation modification
    ):
        """ The class initializer.

        :param id: Quotation id.
        :param customer_id: The individual that created the quotation.
        :param status: Current quotation status.
        :param created: Quotation created timestamp.


        """
        self.id = id
        self.price = price
        self.details = details
        self.owner_id = owner_id
        self.order_id = order_id
        self.status = status
        self.created = created
        self.update_history = update_history
        self.updater_id = updater_id
        # self.new_status = new_status

        # Initialize objects.
        self.repo = repository

    # ---------------------------------------------------------
    #
    def create(self) -> QuotationModel:
        """ Create a new quotation in DB.

        - check if the customer exist(registred) in customer collection
        - Then create the quotation if the customer is registred

        :raise HTTPException [400]: when create quotation in quotations table failed.
        :raise HTTPException [403]: when the requester don't have enough right.
        """
        # Check the existence of the order
        repo = OrdersRepository()
        order = repo.read(self.order_id)
        if not order:
            errmsg = f"Cannot create find the order: {self.order_id}."
            raise HTTPException(status_code=403, detail=errmsg)

        if self.owner_id is not None:
            # check if it is an employee
            # check if the author can perform this operation
            # author must be an employee
            employee_exist = EmployeesRepository().check_employee(self.owner_id)
            if not employee_exist:
                errmsg = f"Operation not allowed."
                raise HTTPException(status_code=403, detail=errmsg)

        # Check if the order status is validated
        if order['status'] != OrderStatus.ORAC:
            errmsg = f"Cannot create an quotation for the order: {self.order_id}. Incorrect Order status"
            raise HTTPException(status_code=403, detail=errmsg)

        # check if there exist a quotation or
        # if quotation exist it must be in cancelled state
        order_quotations = repo.read_order_quotations(self.order_id)
        # logger.debug(f" Order's quotation: {order_quotations}")
        if len(order_quotations) != 0:
            for quotation in order_quotations:
                if quotation['status'] != QuotationStatus.QCAN:
                    errmsg = f"Cannot create an quotation for the order: {self.order_id}. Order already has active quotation"
                    raise HTTPException(status_code=403, detail=errmsg)

        # Create a new Quotation in DB.
        db_quotation = QuotationCreateInternalModel(price=self.price,
                                                    details=self.details,
                                                    order_id=self.order_id,
                                                    owner_id=self.owner_id,
                                                    status=QuotationStatus.QUREV,
                                                    created=datetime.utcnow(),
                                                    update_history=[])
        new_quotation_id = self.repo.create(db_quotation)

        if not new_quotation_id:
            errmsg = f"Create failed for {self.id=} in quotations collection"
            raise HTTPException(status_code=400, detail=errmsg)

        return new_quotation_id

    # ---------------------------------------------------------
    #

    def validate(self) -> bool:
        """ Validate current quotation.

        :raise HTTPException [403]: when cancel request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Quotation update in quotations table failed.
        """

        # check if it is an employee
        # check if the author can perform this operation
        # author must be an employee
        employee_exist = EmployeesRepository().check_employee(self.updater_id)
        if not employee_exist:
            errmsg = f"Operation not allowed. You must be an employee."
            raise HTTPException(status_code=403, detail=errmsg)

        if self.status != QuotationStatus.QUREV:
            errmsg = f'Could not validate quotation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Quotation status in DB.
        response = self.repo.update(
            quotation_id=self.id, new_status=QuotationStatus.QVAL, author_id=self.updater_id)

        if not response:
            errmsg = f"Failed updating {self.id=} in quotations table"
            raise HTTPException(status_code=400, detail=errmsg)

        return response

    # ---------------------------------------------------------
    #

    def cancel(self) -> bool:
        """ Cancel current quotation.

        :raise HTTPException [403]: when cancel request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Quotation update in quotations table failed.
        """
        # check if it is an employee
        # check if the author can perform this operation
        # author must be an employee
        employee_exist = EmployeesRepository().check_employee(self.updater_id)
        if not employee_exist:
            errmsg = f"Operation not allowed. You must be an employee."
            raise HTTPException(status_code=403, detail=errmsg)

        if self.status != QuotationStatus.QUREV:
            errmsg = f'Could not cancel quotation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # Update Quotation status in DB.
        response = self.repo.update(
            quotation_id=self.id, new_status=QuotationStatus.QCAN, author_id=self.updater_id)

        if not response:
            errmsg = f"Failed updating {self.id=} in quotations table"
            raise HTTPException(status_code=400, detail=errmsg)

        return response

    # ---------------------------------------------------------
    #

    def accept(self) -> QuotationModel:
        """ Accept current quotation.

        :raise HTTPException [403]: when cancel request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Quotation update in quotations table failed.
        """
        # check if the author can perform this operation
        # author must be the owner(customer) of the associated order
        repo = OrdersRepository()
        order = repo.read(self.order_id)
        customer_id = order["customer_id"]
        customer_exist = CustomersRepository().check_customer(customer_id)

        if not customer_exist:
            errmsg = f"Customer {customer_id} don't exist"
            raise HTTPException(status_code=403, detail=errmsg)
        if customer_id != self.updater_id:
            errmsg = f"Operation not allowed. You must be the owner of the order"
            raise HTTPException(status_code=403, detail=errmsg)

        if self.status != QuotationStatus.QVAL:
            errmsg = f'Could not accept quotation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # Update Quotation status in DB.
        response = self.repo.update(
            quotation_id=self.id, new_status=QuotationStatus.QACC, author_id=self.updater_id)

        if not response:
            errmsg = f"Failed updating {self.id=} in quotations table"
            raise HTTPException(status_code=400, detail=errmsg)

        # Schedule realisation
        # choose randomly one employee to assign the order to
        list_of_employees = EmployeesRepository().read_all()
        assigned_employee_id = random.choice(
            list_of_employees).get("id")
        # logger.info(f'employee: {assigned_employee_id}')

        service = RealisationsApi(RealisationsRepository())
        payload = RealisationCreateModel(order_id=self.order_id,
                                         employee_id=assigned_employee_id,
                                         created_by=None)
        realisation_id = service.create_realisation(payload.model_dump())
        if not realisation_id:
            errmsg = f"Failed to schedule realisation for this order={self.order_id}"
            raise HTTPException(status_code=400, detail=errmsg)

        # Update order status
        response = repo.update(self.order_id, new_status=OrderStatus.RESC,
                               author_id=customer_id, comment="Quotation accepted")
        if not response:
            errmsg = f"Failed updating {self.id=} in order collection"
            raise HTTPException(status_code=400, detail=errmsg)

        return response

    # ---------------------------------------------------------
    #
    def reject(self) -> QuotationModel:
        """ Reject current quotation.

        :raise HTTPException [403]: when refuse request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Quotation update in quotations table failed.
        """
        # check if the author can perform this operation
        # author must be the owner(customer) of the associated order
        repo = OrdersRepository()
        order = repo.read(self.order_id)
        customer_id = order["customer_id"]
        customer_exist = CustomersRepository().check_customer(customer_id)

        if not customer_exist:
            errmsg = f"Customer: {customer_id} don't exist"
            raise HTTPException(status_code=403, detail=errmsg)
        if customer_id != self.updater_id:
            errmsg = f"Operation not allowed. You must be the owner of the order"
            raise HTTPException(status_code=403, detail=errmsg)

        if self.status != QuotationStatus.QVAL:
            errmsg = f'Could not accept quotation with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Quotation status in DB.
        response = self.repo.update(
            quotation_id=self.id, new_status=QuotationStatus.QREJ, author_id=self.updater_id)

        if not response:
            errmsg = f"Failed updating {self.id=} in quotations collection"
            raise HTTPException(status_code=400, detail=errmsg)

        # Mark the order as cancelled
        response = repo.update(self.order_id, new_status=OrderStatus.ORCA,
                               author_id=order["customer_id"], comment="Quotation rejected")
        if not response:
            errmsg = f"Failed updating {self.id=} in order collection"
            raise HTTPException(status_code=400, detail=errmsg)

        return response
