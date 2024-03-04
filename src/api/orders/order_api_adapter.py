
from datetime import datetime
import json

# Third party modules
from fastapi import HTTPException
from pydantic import UUID4
from typing import List

# Local modules
from .order_data_adapter import OrdersRepository
from .models import OrderCreateModel, OrderModel
from .order_api_logic import OrderApiLogic


# ------------------------------------------------------------------------
#
class OrdersApi:
    """
    This class implemnts the Web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: OrdersRepository):
        """ The class initializer.

        :param repository: Data layer handler object
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    def _order_of(self, order_id: str) -> OrderModel:
        """ Return specified order.

        :param order_id: order id for order to find.
        :return: Found order object.
        :raise HTTPException [404]: when order not found in DB.
        """
        db_order = self.repo.read(order_id)

        if not db_order:
            errmsg = f"{order_id} not found in DB api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_order

    # ---------------------------------------------------------
    #

    def get_order(self, order_id: str) -> OrderModel:
        """ Return specified order. 

        :param order_id: order id for order to find.
        :return: Found order object.
        :raise HTTPException [404]: when order not found in DB api_db.orders.
        """
        db_order = self._order_of(order_id)

        return db_order

    # ---------------------------------------------------------
    #

    def create_order(self, payload: OrderCreateModel) -> OrderModel:
        """ Create a new order in DB.

        :param payload: order payload.
        :return: Created order object.
        :raise HTTPException [400]: when create order in DB api_db.orders failed.
        """
        print(payload)
        print(type(payload))
        
        service = OrderApiLogic(
            repository=self.repo,
            service=payload['service'],
            description=payload['description'],
            customer_id=payload['customer_id']
        )
        return service.create()       
        #return self.repo.create(payload)

    # ---------------------------------------------------------
    #

    def list_orders(self) -> List[OrderModel]:
        """ list all existing orders in DB api_db.orders.

        :return: list of found orders
        """

        db_orders = self.repo.read_all()

        return db_orders
    

    # ---------------------------------------------------------
    #

    def cancel_order(self, order_id: str, author_id: str) -> OrderModel:
        """ Cancel specified order (will be done by customer).

        :param order_id: id for order to cancel.
        :return: Found Order object.
        :raise HTTPException [400]: when failed to update DB api_db.orders.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """

        # _order_of raise exception if the order is not found
        db_order = self._order_of(order_id)

        order = OrderApiLogic(
            repository=self.repo,
            id=db_order['id'],
            service=db_order['service'],
            description=db_order['description'],
            customer_id=db_order['customer_id'],
            status=db_order['status'],
            created=db_order['created'],
            author_id=author_id)
        return order.cancel()
    # ---------------------------------------------------------
    #

    def validate_order(self, order_id: str, author_id: str) -> OrderModel:
        """ Validate specified order (will be done by customer).

        :param order_id: id for order to cancel.
        :return: Found Order object.
        :raise HTTPException [400]: when failed to update DB api_db.orders.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """

        # _order_of raise exception if the order is not found
        db_order = self._order_of(order_id)

        order = OrderApiLogic(
            repository=self.repo,
            id=db_order['id'],
            service=db_order['service'],
            description=db_order['description'],
            customer_id=db_order['customer_id'],
            status=db_order['status'],
            created=db_order['created'],
            author_id=author_id)
        return order.validate()

     # ---------------------------------------------------------
    #

    def reject_order(self, order_id: str, author_id: str) -> OrderModel:
        """ Reject specified order (will be done by customer).

        :param order_id: id for order to cancel.
        :return: Found Order object.
        :raise HTTPException [400]: when failed to update DB api_db.orders.
        :raise HTTPException [404]: when Order not found in DB api_db.orders.
        """

        # _order_of raise exception if the order is not found
        db_order = self._order_of(order_id)

        order = OrderApiLogic(
            repository=self.repo,
            id=db_order['id'],
            service=db_order['service'],
            description=db_order['description'],
            customer_id=db_order['customer_id'],
            status=db_order['status'],
            created=db_order['created'],
            author_id=author_id)
        return order.reject()
