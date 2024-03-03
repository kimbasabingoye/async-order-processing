
# Third party modules
from fastapi import HTTPException
from bson import ObjectId
from pydantic import UUID4
from typing import List

# Local modules
from .models import CustomerCreateModel, CustomerModel, CustomersCollection
from ..database import db, from_mongo


class CustomersRepository:
    """ This class implements the data layer adapter (the CRUD operations).

    The Order object is cached in Redis. This is handled by the read, update
    and delete methods.
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    def _read(customer_id: UUID4) -> CustomerModel:
        """ Read Customer for matching index key from DB collection customers.

        :param key: Index key.
        :return: Found Customer.
        """

        response = db.customers.find_one({"_id": ObjectId(customer_id)})

        return from_mongo(response)

    # ---------------------------------------------------------
    #

    def read(self, customer_id: str) -> CustomerModel:
        """ Read Customer for matching index key from DB collection customers.

        :param key: Index key.
        :return: Found Customer.
        """

        response = self._read(customer_id=customer_id)

        return response

    # ---------------------------------------------------------
    #

    def create(self, payload: CustomerCreateModel) -> str:
        """ Create Customer in customers collections.

        :param payload: New customer payload.
        :return: Created customer.
        """
        try:
            new_customer = db.customers.insert_one(payload)
            # created_customer = self.read(str(new_customer.inserted_id))
            return str(new_customer.inserted_id)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500,
                                detail=f"Customer creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[CustomerModel]:
        """ Read Customer in customer collection.

        :return: list of found customers.
        """

        customers = db.customers.find({})

        return list(map(from_mongo, customers))
