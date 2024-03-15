from typing import List
from .customer_data_adapter import CustomersRepository
from .models import CustomerModel, CustomerCreateModel
from ..base_api_adapter import BaseAPIAdapter


class CustomersAPIAdapter(BaseAPIAdapter):
    """
    API adapter for handling customer-related operations.
    """

    def __init__(self, repository: CustomersRepository):
        super().__init__(repository)

    def get_customer(self, customer_id: str) -> CustomerModel:
        """Get a customer by ID."""
        return self.get_obj(customer_id)

    def create_customer(self, payload: CustomerCreateModel) -> str:
        """Create a new customer."""
        return self.create_obj(payload)

    def list_customers(self) -> List[CustomerModel]:
        """List all customers."""
        return self.read_all_obj()
