
from datetime import datetime
import json

# Third party modules
from fastapi import HTTPException
from pydantic import UUID4

# Local modules
from .customer_data_adapter import CustomersRepository
from .models import CustomersCollection, CustomerCreateModel, CustomerModel


# ------------------------------------------------------------------------
#
class CustomersApi:
    """
    This class implemnts the Web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: CustomersRepository):
        """ The class initializer.

        :param repository: Data layer handler object
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    def _customer_of(self, customer_id: UUID4) -> CustomerModel:
        """ Return specified customer.

        :param customer_id: customer id for customer to find.
        :return: Found customer object.
        :raise HTTPException [404]: when customer not found in DB.
        """
        db_customer = self.repo.read(customer_id)

        if not db_customer:
            errmsg = f"{customer_id} not found in DB api_db.orders"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_customer

    # ---------------------------------------------------------
    #

    def get_customer(self, customer_id: str) -> CustomerModel:
        """ Return specified customer. 

        :param customer_id: customer id for customer to find.
        :return: Found customer object.
        :raise HTTPException [404]: when customer not found in DB api_db.customers.
        """
        db_customer = self._customer_of(customer_id)

        return db_customer

    # ---------------------------------------------------------
    #

    def create_customer(self, payload: CustomerCreateModel) -> CustomerModel:
        """ Create a new customer in DB.

        :param payload: customer payload.
        :return: Created customer object.
        :raise HTTPException [400]: when create customer in DB api_db.customers failed.
        """

        return self.repo.create(payload=payload)

    # ---------------------------------------------------------
    #

    def list_customers(self) -> CustomersCollection:
        """ list all existing customers in DB api_db.customers.

        :return: list of found customers
        """

        db_customers = self.repo.read_all()

        return db_customers
