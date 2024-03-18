from utils import db, random_date
from utils import QuotationStatus, OrderStatus
from datetime import datetime
from bson import ObjectId
import random
import logging
from enum import Enum

from utils import db
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealisationStatus(str, Enum):
    """ Realisation status changes. """

    RSCH = 'realisationScheduled'
    RSTA = 'realisationStarted'
    RCOM = 'realisationCompleted'


quotations_collection = db["quotations"]
orders_collection = db["orders"]
employees_collection = db["employees"]
realisation_collection = db["realisations"]

def generate_realisations():
    realisations_data = []

    quotations = quotations_collection.find({"status": QuotationStatus.QACC})
    employees_data = list(employees_collection.find({}))

    for quotation in quotations:
        order_id = quotation.get("order_id")
        if not order_id:
            logger.warning(
                "Skipping quotation without order_id: %s", quotation)
            continue

        employee_id = random.choice(employees_data).get("_id")
        assignment_date = random_date(
            quotation["update_history"][-1]["when"], datetime.now())
        start_date = None
        end_date = None

        status = random.choice(
            [RealisationStatus.RSCH, RealisationStatus.RSTA, RealisationStatus.RCOM])

        if status in (RealisationStatus.RSTA, RealisationStatus.RCOM):
            start_date = random_date(assignment_date, datetime.now())
            if status == RealisationStatus.RCOM:
                end_date = random_date(start_date, datetime.now())

        realisation = {
            "order_id": order_id,
            "employee_id": employee_id,
            "status": status,
            "assignment_date": assignment_date,
            "start_date": start_date,
            "end_date": end_date
        }
        realisations_data.append(realisation)

        # Update order status and history
        update_history = []
        if status == RealisationStatus.RSCH:
            update_history.append({
                "new_status": OrderStatus.RESC,
                "when": assignment_date,
                "by": "",
                "comment": ""
            })
        elif status == RealisationStatus.RSTA:
            update_history.extend([
                {"new_status": OrderStatus.RESC,
                    "when": assignment_date, "by": "", "comment": ""},
                {"new_status": OrderStatus.RSTA,
                    "when": start_date, "by": "", "comment": ""}
            ])
        else:
            update_history.extend([
                {"new_status": OrderStatus.RESC,
                    "when": assignment_date, "by": "", "comment": ""},
                {"new_status": OrderStatus.RSTA,
                    "when": start_date, "by": "", "comment": ""},
                {"new_status": OrderStatus.DONE,
                    "when": end_date, "by": "", "comment": ""}
            ])
            order_status = OrderStatus.DONE

        if status == RealisationStatus.RCOM:
            orders_collection.update_one({"_id": order_id}, {
                                         "$set": {"status": OrderStatus.DONE}})
        orders_collection.update_one({"_id": order_id}, {
                                         "$push": {"update_history": {"$each": update_history}}})
        #o = orders_collection.find_one({"_id": order_id})
        #print(f"Order: {o}")

    return realisations_data

r = generate_realisations()

#print(r)

realisation_collection.insert_many(r)
print("Realisation data inserted into MongoDB.")
