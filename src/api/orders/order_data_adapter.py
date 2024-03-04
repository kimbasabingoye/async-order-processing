# BUILTIN modules
from datetime import datetime

# Third party modules
from fastapi import HTTPException, status
from bson import ObjectId
from pydantic import UUID4
from typing import List
from bson import json_util

# Local modules
from .models import OrderCreateModel, OrderModel, OrderStatus, OrderCreateInternalModel, NotFoundError, StateUpdateSchema
from ..database import db, from_mongo


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

        return OrderModel(**response).dict()

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

    def create(self, payload: OrderCreateInternalModel) -> OrderModel:
        """ Create Order in orders collections.

        :param payload: New order payload.
        :return: Created order.
        """
        try:
            new_order = db.orders.insert_one(payload.model_dump())
            created_order = self.read(str(new_order.inserted_id))
            # return str(new_order.inserted_id)
            return created_order
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500,
                                detail=f"Order creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[OrderModel]:
        """ Read Order in order collection.

        :return: list of found orders.
        """
        response  = []
        orders = db.orders.find({})

        for order in orders:
            order = OrderModel(**from_mongo(order)).dict()
            response.append(order)

        return response

    # ---------------------------------------------------------
    #

    def update(self, order_id: str, new_status: OrderStatus, author_id: str) -> OrderModel:
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
            by=author_id)

        db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$push": {"update_history": update_history_entry.model_dump()}}
        )

        updated_order = self._read(order_id=order_id)

        return updated_order
