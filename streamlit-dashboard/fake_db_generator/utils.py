import random
from datetime import datetime, timedelta
from bson import ObjectId
from faker import Faker
from enum import Enum
from pydantic import BaseModel

from pymongo import MongoClient

client = MongoClient("mongodb://mongoadmin:secret@localhost:27017/")

db = client.get_database("TestAsyncOrderProcDB")



# ---------------------------------------------------------
#
class OrderStatus(str, Enum):
    """ Order status changes.

    CREA -> ORAC/OREJ/ORCA -> QGEN -> QVAL/QREJ -> RESC -> DONE

    """
    UREV = 'underReview'            # OrderService
    ORAC = 'orderAccepted'          # OrderService
    OREJ = 'orderRejected'          # OrderService
    ORCA = 'orderCancelled'         # OrderService
    RESC = 'realisationScheduled'   # OrderService
    RSTA = 'realisationStarted'   # OrderService
    DONE = 'delivered'              # OrderService


class QuotationStatus(str, Enum):
    """Quotation status changes."""
    QGEN = 'quotationGenerated'     # QuotationService
    QVAL = 'quotationValidated'     # QuotationService
    QCAN = 'quotationCancelled'     # QuotationService
    QREJ = 'quotationRejected'      # QuotationService
    QACC = 'quotationAccepted'      # QuotationService


# Function to generate a random email
def generate_email(first_name, last_name):
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com']
    return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"


# Function to generate a random date within a range
def random_date(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

"""
class StateUpdateSchema(BaseModel):
    Representation of an Order status history in the system. 
    new_status: OrderStatus
    when: datetime
    by: ObjectId
    comment: str = ""

    def dict(self):
        return {
            'new_status': self.new_status,
            'when': self.when.isoformat(),
            'by': self.by,
            'comment': self.comment
        }
"""
def read(order_id: str):
    """ Read Order for matching index key from DB collection orders.

        :param key: Index key.
        :return: Found Order.
        """

    response = db.orders.find_one({"_id": ObjectId(order_id)})
    return response

def update(self, order_id: str, new_status: OrderStatus, d: datetime, author_id: str, comment: str = ""):
    """ Update Order in DB collection api_db.orders.

    :param order_id: id of the order to update.
    :param new_status: The new status of the order.
    :param autor_id: id of who make the modification
    :return: updated order.
    """
    order = read(order_id=order_id)

    db.orders.update_one({"_id": ObjectId(order_id)}, {
        "$set": {"status": new_status.value}})

    # Update the update history
    update_history_entry = {
        "new_status": new_status,
        "when": datetime.utcnow(),
        "by":author_id,
        "comment": comment
    }

    db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$push": {"update_history": update_history_entry.model_dump()}}
    )

    updated_order = self.read(order_id=order_id)

    return updated_order


# Exemple d'utilisation
start_date_str = "2024-02-14T02:58:28"
end_date = datetime.now()

created = random_date(start_date_str, end_date)
#print(created)
