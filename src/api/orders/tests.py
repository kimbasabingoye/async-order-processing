from pydantic import UUID4, BaseModel, ConfigDict, Field, EmailStr
import uuid
from typing import Callable, List
from bson import ObjectId
from fastapi import HTTPException
from enum import Enum

# Third party modules
from pymongo import MongoClient

client = MongoClient("mongodb://mongoadmin:secret@localhost:27017/")

db = client.get_database("AsyncOrderProcDB")

# ------------------------------------------------------------------------
#


def from_mongo(data: dict):
    """ Convert "_id" (str object) into "id" str. """

    if not data:
        return data

    if '_id' in data:
        data['id'] = str(data.pop('_id'))
        return data

# ---------------------------------------------------------
#


class CustomerCreateModel(BaseModel):
    """ Representation of an data required when creating customer in the system. """
    first_name: str
    last_name: str
    email: EmailStr


# ---------------------------------------------------------
#
class CustomerModel(CustomerCreateModel):
    """ Representation of an Customer in the system. """
    id: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)


class CustomersCollection(BaseModel):
    """
    A container holding a list of `CustomerModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    customers: List[CustomerModel]


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

    def read(self, customer_id: UUID4) -> CustomerModel:
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
    @staticmethod
    def read_all() -> CustomersCollection:
        """ Read Orders in orders table.

        Sorted on creation timestamp in descending order.
        :param skip: skip.
        :param limit: limit.
        :return: list of found Orders.
        """

        customers = db.customers.find({})

        return list(map(from_mongo, customers))


class Services(Enum):
    """ Représentation des services valides dans le système. """
    web_site = 'Make a web site'
    mobile_app = 'Make a mobile app'
    desktop_app = 'Make a desktop app'


class ServicePrices:
    """ Classe représentant les prix des services dans le système. """

    def __init__(self):
        self.prices = {
            'web_site': 5000,
            'mobile_app': 8000,
            'desktop_app': 10000
        }

    def get_price(self, service):
        """ Obtenir le prix associé à un service donné. """
        return self.prices.get(service.name, None)


# Exemple d'utilisation :
response = db.quotations.find(
    {"order_id": "65e735853aa841d1d1207acd"})

for q in response:
    print(q)