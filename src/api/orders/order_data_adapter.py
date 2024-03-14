# BUILTIN modules
from typing import List

# Local modules
from src.api.orders.models import OrderModel, OrderStatus
from src.api.database import db, PyObjectId, BaseRepositoryWithStatus
from src.api.quotations.models import QuotationModel
from ..quotations.quotation_data_adapter import QuotationsRepository


class OrdersRepository(BaseRepositoryWithStatus[OrderModel]):
    """Repository for managing orders."""

    def __init__(self):
        super().__init__(db, "orders")

    def read(self, obj_id: str) -> OrderModel:
        """Read object for matching index key from DB collection."""
        # Call parent class's read method
        obj = super().read(obj_id)
        return OrderModel(**obj).to_dict()

    def update(self, order_id: str, new_status: OrderStatus, author_id: str, comment: str = "") -> bool:
        """Update Order."""
        return super().update(order_id, new_status, author_id, comment)

    def read_all(self) -> List[OrderModel]:
        """Read all objects from the collection."""
        # Call parent class's read_all method
        objs = super().read_all()

        # Transform each object to OrderModel and return a list
        return [OrderModel(**obj).to_dict() for obj in objs]

    def read_order_quotations(self, order_id: str) -> List[QuotationModel]:
        """Read quotations for the specified order."""
        q_repo = QuotationsRepository()
        return q_repo.read_order_quotations(order_id)

    def is_validated(self, order_id: PyObjectId) -> bool:
        """Check if an order is accepted.

        :param order_id: The ID of the order to check.
        :return: True if the order is accepted, False otherwise.
        """
        # Get the status of the order
        status = self.get_status(order_id)

        # Check if the status is OrderStatus.ACCEPTED
        return status == OrderStatus.ORAC
