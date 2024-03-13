# BUILTIN modules
from datetime import datetime
from typing import Optional, List

# Third party modules
from fastapi import HTTPException

# Local modules
from .models import Services, OrderStatus, OrderModel, OrderCreateModel, StateUpdateSchema, OrderCreateInternalModel, ServicePrices
from .order_data_adapter import OrdersRepository
from ..quotations.quotation_api_logic import QuotationApiLogic
from ..quotations.quotation_data_adapter import QuotationsRepository
from ..quotations.quotation_api_adapter import QuotationsApi
from ..quotations.models import QuotationCreateModel, QuotationStatus
from ..customers.customer_data_adapter import CustomersRepository
from ..employees.employee_data_adapter import EmployeesRepository


# ------------------------------------------------------------------------
#
class OrderApiLogic:
    """
    This class implements the Order web API business logic layer.
    """

    # ---------------------------------------------------------
    #
    def __init__(
            self,
            repository: OrdersRepository,
            service: Services = None,
            description: str = None,
            customer_id: str = None,
            id: str = None,
            status: OrderStatus = None,
            created: datetime = None,
            update_history: List[StateUpdateSchema] = None,
            author_id: int = None,  # for order modification
            comment: str = ""
            # new_status: OrderStatus = None  # for order modification
    ):
        """ The class initializer.

        :param id: Order id.
        :param service: Service ordered.
        :param description: more detail about the service.
        :param customer_id: The individual that created the order.
        :param status: Current order status.
        :param created: Order created timestamp.


        """
        self.id = id
        self.service = service
        self.description = description
        self.customer_id = customer_id
        self.status = status
        self.created = created
        self.update_history = update_history
        self.author_id = author_id
        self.comment = comment
        # self.new_status = new_status

        # Initialize objects.
        self.repo = repository

    # ---------------------------------------------------------
    #
    def create(self) -> OrderModel:
        """ Create a new order in DB.

        - check if the customer exist(registred) in customer collection
        - Then create the order if the customer is registred

        :raise HTTPException [400]: when create order in orders collections failed.
        :raise HTTPException [403]: when customer don't exist in customers collection.
        """

        # Check the existence of the customer
        # Try to get the customer
        # if customer not found an exception will be raised
        customer_exist = CustomersRepository().check_customer(self.customer_id)

        if not customer_exist:
            errmsg = f"Cannot create an order for the customer: {self.customer_id}. Customer don't exist"
            raise HTTPException(status_code=403, detail=errmsg)

        # Create a new Order in DB.
        db_order = OrderCreateInternalModel(service=self.service,
                                            description=self.description,
                                            customer_id=self.customer_id,
                                            status=OrderStatus.UREV,
                                            created=datetime.utcnow(),
                                            update_history=[])
        new_order_id = self.repo.create(db_order)

        if not new_order_id:
            errmsg = f"Create failed for {self.id=} in orders collection"
            raise HTTPException(status_code=400, detail=errmsg)

        return new_order_id

    # ---------------------------------------------------------
    #

    def cancel(self) -> bool:
        """ Cancel current order. 
        Only the owner of the quotation is allowed to do this action

        :raise HTTPException [403]: when cancel request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Order update in orders table failed.
        """

        if self.status in (OrderStatus.RESC, OrderStatus.REST, OrderStatus.RECO, OrderStatus.ORCA):
            errmsg = f'Could not cancel order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=403, detail=errmsg)

        # check if the author can perform this operation
        customer_exist = CustomersRepository().check_customer(self.customer_id)
        if not customer_exist:
            errmsg = f"You are not allowed to perform this operation"
            raise HTTPException(status_code=403, detail=errmsg)

        # author must be the owner(customer) of the order
        if self.customer_id != self.author_id:
            errmsg = f"Operation not allowed. You must be the owner of the order"
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Order status in DB.
        updated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.ORCA, author_id=self.author_id, comment=self.comment)

        if not updated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        return True

    # ---------------------------------------------------------
    #
    def validate(self) -> bool:
        """ Validate current order.
        Only employees are allowed to perform this action

        :raise HTTPException [403]: when validate request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Order update in orders table failed.
        """

        if self.status != OrderStatus.UREV:
            errmsg = f'Could not validate order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # check if the author can perform this operation
        # author must be an employee
        employee_exist = EmployeesRepository().check_employee(self.author_id)

        if not employee_exist:
            errmsg = f"You are not allowed to perform this operation."
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Order status in DB.
        validated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.ORAC, author_id=self.author_id, comment=self.comment)

        if not validated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        # generate quotation
        service = QuotationsApi(QuotationsRepository())
        payload = QuotationCreateModel(
            price=ServicePrices().get_price(self.service),
            order_id=self.id,
            details="",
            owner_id=None
        )
        quotation_id = service.create_quotation(payload.model_dump())
        if not quotation_id:
            errmsg = f"Failed generating quotation for this order={self.id}"
            raise HTTPException(status_code=400, detail=errmsg)

        return True

    # ---------------------------------------------------------
    #
    def reject(self) -> bool:
        """ Reject current order.
        Only employees are allowed to perform this action

        :raise HTTPException [403]: when reject request came too late.
        :raise HTTPException [403]: when the requester don't have enough right.
        :raise HTTPException [400]: when Order update in orders collection failed.
        """

        if self.status != OrderStatus.UREV:
            errmsg = f'Could not reject order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # check if the author can perform this operation
        # author must be an employee
        employee_exist = EmployeesRepository().check_employee(self.author_id)

        if not employee_exist:
            errmsg = f"Operation not allowed. You must be an employee."
            raise HTTPException(status_code=403, detail=errmsg)

        # Update Order status in DB.
        updated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.OREJ, author_id=self.author_id, comment=self.comment)

        if not updated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        # send notification to customer

        return True
    
    
