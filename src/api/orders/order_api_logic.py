# BUILTIN modules
from datetime import datetime
from typing import Optional, List

# Third party modules
from fastapi import HTTPException

# Local modules
from .models import Services, OrderStatus, OrderModel, OrderCreateModel, StateUpdateSchema, OrderCreateInternalModel
from .order_data_adapter import OrdersRepository


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
            customer_id: int = None,
            id: int = None,
            status: OrderStatus = None,
            created: datetime = None,
            update_history: List[StateUpdateSchema] = None,
            author_id: int = None,  # for order modification
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
        # self.new_status = new_status

        # Initialize objects.
        self.repo = repository

    # ---------------------------------------------------------
    #
    def create(self) -> OrderModel:
        """ Create a new order in DB.

        - check if the customer exist(registred) in customer collection
        - Then create the order if the customer is registred

        :raise HTTPException [400]: when create order in orders table failed.
        """

        # Check the existence of the customer

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

    def cancel(self) -> OrderModel:
        """ Cancel current order.

        :raise HTTPException [400]: when cancel request came too late.
        :raise HTTPException [400]: when Order update in orders table failed.
        """

        if self.status in (OrderStatus.RESC, OrderStatus.DONE, OrderStatus.ORCA):
            errmsg = f'Could not cancel order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # Update Order status in DB.
        updated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.ORCA, author_id=self.author_id)

        if not updated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        return updated_order

    # ---------------------------------------------------------
    #
    def validate(self) -> OrderModel:
        """ Validate current order.

        :raise HTTPException [400]: when cancel request came too late.
        :raise HTTPException [400]: when Order update in orders table failed.
        """

        if self.status not in (OrderStatus.UREV, OrderStatus.ORAC):
            errmsg = f'Could not validate order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # check the author right

        # Update Order status in DB.
        validated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.ORAC, author_id=self.author_id)

        if not validated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        # generate quotation

        # return order + quotation

        return validated_order

    # ---------------------------------------------------------
    #
    def reject(self) -> OrderModel:
        """ Reject current order.

        NOTE: this can only be done before a driver is available (status DRAV).

        :raise HTTPException [400]: when cancel request came too late.
        :raise HTTPException [400]: when Order update in orders table failed.
        """

        if self.status not in (OrderStatus.UREV, OrderStatus.ORAC):
            errmsg = f'Could not reject order with id {self.id}. Current status: {self.status}'
            raise HTTPException(status_code=400, detail=errmsg)

        # Update Order status in DB.
        updated_order = self.repo.update(
            order_id=self.id, new_status=OrderStatus.OREJ, author_id=self.author_id)

        if not updated_order:
            errmsg = f"Failed updating {self.id=} in orders table"
            raise HTTPException(status_code=400, detail=errmsg)

        return updated_order
