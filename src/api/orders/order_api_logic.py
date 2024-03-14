from datetime import datetime
from typing import List

from fastapi import HTTPException
from loguru import logger

from .models import OrderStatus, OrderModel, OrderCreateInternalModel
from ..database import  UpdateModel, PyObjectId
from .order_data_adapter import OrdersRepository
from ..quotations.quotation_api_adapter import QuotationsApi
from ..quotations.models import QuotationCreateModel, QuotationModel
from ..quotations.quotation_data_adapter import QuotationsRepository
from .services import get_service_prices
from ..utils import validate_user_is_customer, validate_user_is_employee, validate_order_exist


class OrderApiLogic:
    """
    This class implements the Order endpoints business logic layer.
    """

    def __init__(self, repository: OrdersRepository):
        """Class initializer."""
        self.repo = repository

    def get(self, order_id: PyObjectId) -> OrderModel:
        """Read order in DB."""
        validate_order_exist(order_id)
        return self.repo.read(order_id)
    
    def get_order_quotations(self, order_id: PyObjectId) -> List[QuotationModel]:
        """List all quotations for specified order."""

        validate_order_exist(order_id)

        return self.repo.read_order_quotations(order_id)


    def create(self, payload: OrderCreateInternalModel) -> OrderModel:
        """Create a new order in DB."""

        customer_id = payload.get("customer_id")
        validate_user_is_customer(customer_id)

        db_order = OrderCreateInternalModel(
            service=payload.get("service"),
            description=payload.get("description"),
            customer_id=customer_id,
            status=OrderStatus.UREV,
            created=datetime.utcnow(),
            update_history=[]
        )
        new_order_id = self.repo.create(db_order.model_dump())

        if not new_order_id:
            raise HTTPException(
                status_code=400, detail=f"Failed to create order")

        return new_order_id

    def cancel(self, payload: UpdateModel) -> bool:
        """Cancel current order."""
        order_id = payload.get('obj_id')
        author_id = payload.get('author_id')
        comment = payload.get('comment')

        if not order_id or not author_id:
            raise HTTPException(
                status_code=400, detail="Order ID and author ID are required")

        validate_order_exist(order_id)

        order = self.repo.read(order_id)

        if order['status'] in {OrderStatus.RESC, OrderStatus.REST, OrderStatus.RECO, OrderStatus.ORCA}:
            raise HTTPException(
                status_code=403, detail=f"Could not cancel order with ID {order_id}. Current status: {order['status']}")

        validate_user_is_customer(author_id)

        if order.get('customer_id') != author_id:
            raise HTTPException(
                status_code=403, detail=f"Operation not allowed. You must be the owner of the order")

        if not self.repo.update(order_id=order_id, new_status=OrderStatus.ORCA, author_id=author_id, comment=comment):
            raise HTTPException(
                status_code=400, detail=f"Failed updating order with ID {order_id}")

        return True

    def validate(self, payload: UpdateModel) -> bool:
        """Validate current order."""
        order_id = payload.get('obj_id')
        author_id = payload.get('author_id')
        comment = payload.get('comment')

        if not order_id or not author_id:
            raise HTTPException(
                status_code=400, detail="Order ID and author ID are required")

        validate_order_exist(order_id)

        order = self.repo.read(order_id)

        if order['status'] != OrderStatus.UREV:
            raise HTTPException(
                status_code=400, detail=f"Could not validate order with ID {order_id}. Current status: {order['status']}")

        validate_user_is_employee(author_id)

        if not self.repo.update(order_id=order_id, new_status=OrderStatus.ORAC, author_id=author_id, comment=comment):
            raise HTTPException(
                status_code=400, detail=f"Failed updating order with ID {order_id}")

        # Generate quotation
        product = order.get('service')
        product_price = get_service_prices(product)
        logger.debug(f"Service: {product}")
        logger.debug(f"Type: {type(order.get('service'))}")
        logger.debug(f"Price: {product_price}")
        service = QuotationsApi(QuotationsRepository())
        payload = QuotationCreateModel(
            price=product_price,
            order_id=order_id,
            details="Generated",
            owner_id=None
        )
        quotation_id = service.create_quotation(payload.model_dump())
        if not quotation_id:
            raise HTTPException(
                status_code=400, detail=f"Failed generating quotation for order with ID {order_id}")
            # rollback

        return True

    def reject(self, payload: UpdateModel) -> bool:
        """Reject current order."""
        order_id = payload.get('obj_id')
        author_id = payload.get('author_id')
        comment = payload.get('comment')

        if not order_id or not author_id:
            raise HTTPException(
                status_code=400, detail="Order ID and author ID are required")

        validate_order_exist(order_id)

        order = self.repo.read(order_id)

        if order['status'] != OrderStatus.UREV:
            raise HTTPException(
                status_code=400, detail=f"Could not reject order with ID {order_id}. Current status: {order['status']}")

        validate_user_is_employee(author_id)

        if not self.repo.update(order_id=order_id, new_status=OrderStatus.OREJ, author_id=author_id, comment=comment):
            raise HTTPException(
                status_code=400, detail=f"Failed updating order with ID {order_id}")

        return True
