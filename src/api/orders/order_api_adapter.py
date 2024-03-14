
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
from ..quotations.models import QuotationModel
from ..database import PyObjectId, UpdateModel

from typing import List
from .order_data_adapter import OrdersRepository
from .models import OrderModel, OrderCreateModel
from ..base_api_adapter import BaseAPIAdapter


class OrdersAPIAdapter(BaseAPIAdapter):
    """
    API adapter for handling order-related operations.
    """

    def __init__(self, repository: OrdersRepository):
        super().__init__(repository)

    def get_order(self, order_id: str) -> OrderModel:
        """Get an order by ID."""
        return OrderApiLogic(repository=self.repo).get(order_id)

    def list_orders(self) -> List[OrderModel]:
        """List all orders."""
        return super().read_all_obj()

    def list_order_quotations(self, order_id: str) -> List[QuotationModel]:
        """List all quotations for specified order."""
        return OrderApiLogic(self.repo).get_order_quotations(order_id)

    def create_order(self, payload: OrderCreateModel) -> PyObjectId:
        """Create a new order."""
        return OrderApiLogic(repository=self.repo).create(payload)

    def cancel_order(self, payload: UpdateModel) -> bool:
        """Cancel specified order."""
        return OrderApiLogic(repository=self.repo,).cancel(payload)

    def validate_order(self, payload: UpdateModel) -> bool:
        """Validate specified order (will be done by order)."""
        return OrderApiLogic(repository=self.repo).validate(payload)

    def reject_order(self, payload: UpdateModel) -> bool:
        """ Reject specified order (will be done by order)."""
        return OrderApiLogic(repository=self.repo).reject(payload)
