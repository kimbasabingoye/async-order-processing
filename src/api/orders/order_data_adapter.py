# BUILTIN modules
from datetime import datetime

# Third party modules
from fastapi import HTTPException, status
from bson import ObjectId
from pydantic import UUID4
from typing import List
from bson import json_util

# Local modules
from src.api.orders.models import OrderCreateModel, OrderModel, OrderStatus, OrderCreateInternalModel, NotFoundError, StateUpdateSchema
from src.api.database import db, from_mongo, PyObjectId
from src.api.quotations.models import QuotationModel
from ..quotations.quotation_data_adapter import QuotationsRepository


class OrdersRepository:
    """ This class implements the data layer adapter (the CRUD operations).
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    def _read(order_id: str) -> OrderModel:
        """ Read Order for matching index key from DB collection orders.

        :param key: Index key.
        :return: Found Order.
        """

        response = from_mongo(db.orders.find_one({"_id": ObjectId(order_id)}))

        if response:
            return OrderModel(**response).dict()

    # ---------------------------------------------------------
    #

    def check_order(self, order_id: str) -> bool:
        """Check if the order exists.

        :param order_id: The ID of the order to check.
        :return: True if the order exists, False otherwise.
        """
        response = self._read(order_id)

        if response:
            return True

        return False

    def get_status(self, order_id: str) -> OrderStatus:
        """ Return order status.

        :param key: Index key.
        :return: True if customer is found and False if not.
        """
        order = self._read(order_id)

        if order:
            return order["status"]
        else:
            errmsg = f"Cannot create find the order: {self.order_id}."
            raise HTTPException(status_code=403, detail=errmsg)

    # ---------------------------------------------------------
    #
    def is_validated(self, order_id: PyObjectId) -> bool:
        """Check if a order is accepted.

        :param order_id: The ID of the order to check.
        :return: True if the order is accepted, False otherwise.
        """
        # Get the status of the order
        status = self.get_status(order_id)

        # Check if the status is orderStatus.ACCEPTED
        return status == OrderStatus.ORAC

    # ---------------------------------------------------------
    #

    def read(self, order_id: str) -> OrderModel:
        """ Read Order for matching index key from DB collection orders.

        :param key: Index key.
        :return: Found Order.
        """

        response = self._read(order_id=order_id)

        return response

    # ---------------------------------------------------------
    #

    def create(self, payload: OrderCreateInternalModel) -> bool:
        """ Create Order in orders collections.

        :param payload: New order payload.
        :return: Created order.
        """
        try:
            new_order = db.orders.insert_one(payload.model_dump())
            return str(new_order.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"Order creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[OrderModel]:
        """ Read Order in order collection.

        :return: list of found orders.
        """
        response = []
        orders = db.orders.find({})

        for order in orders:
            order = OrderModel(**from_mongo(order)).dict()
            response.append(order)

        return response
    
    # ---------------------------------------------------------
    #
    def read_order_quotations(self, order_id: str) -> List[QuotationModel]:
        """ Read quotation for specified order.

        :return: list of found quotations.
        """
        q_repo = QuotationsRepository()
        quotations = q_repo.read_order_quotations(order_id)

        return quotations

    
    # ---------------------------------------------------------
    #

    def update(self, order_id: str, new_status: OrderStatus, author_id: str, comment: str = "") -> bool:
        """ Update Order in DB collection api_db.orders.

        :param order_id: id of the order to update.
        :param new_status: The new status of the order.
        :param autor_id: id of who make the modification
        :return: updated order.
        """
        order = self._read(order_id=order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NotFoundError().detail)

        db.orders.update_one({"_id": ObjectId(order_id)}, {
            "$set": {"status": new_status.value}})

        # Update the update history
        update_history_entry = StateUpdateSchema(
            new_status=new_status,
            when=datetime.utcnow(),
            by=author_id,
            comment=comment)

        response = db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$push": {"update_history": update_history_entry.model_dump()}}
        )

        return response.raw_result['updatedExisting']
