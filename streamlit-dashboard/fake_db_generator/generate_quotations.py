import random
import json
from utils import OrderStatus, QuotationStatus, random_date
from datetime import datetime
from bson import ObjectId


def generate_quotation_for_accepted_orders(employees_data, orac_orders):
    # Generate one quotation by system per order
    qgen_q = []
    qval_q = []
    qcan_q = []

    for order in orac_orders:
        #order = json.loads(order)
        # Determine the quotation status
        # Choose a random status between QGEN, QVAL, and QCAN
        status = random.choice(
            [QuotationStatus.QGEN, QuotationStatus.QVAL, QuotationStatus.QCAN])

        # Generate quotation details
        price = random.randint(100, 50000)
        details = f"Details for Quotation for Order {order['_id']}"
        created = random_date(order["created"], datetime.now())
        when = random_date(created, datetime.now())

        # Choose updater (employee)
        if status != QuotationStatus.QGEN:
            updater = random.choice(employees_data)["_id"]
            up_hist = [{
                "new_status": status,
                "when": when,
                "by": updater,
                "comment": f"Update status set to {status}"
            }]
        else:
            up_hist = []

        # Append quotation data
        q = {
            "_id": str(ObjectId()),
            "price": price,
            "status": status,
            "update_history": up_hist,
            "created": created,
            "order_id": order["_id"],
            "details": details,
            "owner_id": None
        }
        #q = json.dumps(q)
        if status == QuotationStatus.QGEN:
            qgen_q.append(q)
        elif status == QuotationStatus.QVAL:
            qval_q.append(q)
        else:
            qcan_q.append(q)

            # Generate quotation details
            price = random.randint(100, 50000)
            details = f"Details for Quotation for Order {order['_id']}"
            created = random_date(when, datetime.now())
            when = random_date(created, datetime.now())
            status = QuotationStatus.QVAL

            # Choose updater (employee)
            updater = random.choice(employees_data)["_id"]
            up_hist = [{
                "new_status": status,
                "when": when,
                "by": updater,
                "comment": f"Update status set to {status}"
            }]

            new_q = {
                "_id": str(ObjectId()),
                "price": price,
                "status": status,
                "update_history": up_hist,
                "created": created,
                "order_id": order["_id"],
                "details": details,
                "owner_id": updater
            }
            #new_q = json.dumps(new_q)
            qval_q.append(new_q)

    return qgen_q, qval_q, qcan_q


def generate_customer_action_on_quotations(qval_q):
    if not qval_q:
        return
    for q in qval_q:
        #print(f"BEFORE {q}")
        # print(type(q))
        #q = json.loads(q)
        # Determine the quotation status
        # Choose a random status between QGEN, QVAL, and QCAN
        status = random.choice([QuotationStatus.QREJ, QuotationStatus.QACC])
        # Generate quotation details
        #up_his = q["update_history"]
        #print(f"#################Quot: {up_his}")
        # print("KIIIIIIIIIIIIIIIII", q["update_history"][-1]["when"])
        when = random_date(q["update_history"][-1]["when"], datetime.now())
        updater = "owner"
        comment = ""

        q["status"] = status
        q["update_history"].append({
            "new_status": status,
            "when": when,
            "by": updater,
            "comment": comment
        })
        #print(f"AFTER: {q}")
        #q = json.dumps(q)
        #qval_q.append(q)
    return qval_q

"""
employees_data = [
    {
        "_id": "65e88a72295cd162063ed540",
        "first_name": "Dalton",
        "last_name": "Klein",
        "email": "dalton.klein@example.com"
    }, {
        "_id": "65e88a72295cd162063ed4dc",
        "first_name": "Phillip",
        "last_name": "Castillo",
        "email": "phillip.castillo@gmail.com"
    }, {
        "_id": "65e88a72295cd162063ed4dc",
        "first_name": "Phillip",
        "last_name": "Castillo",
        "email": "phillip.castillo@gmail.com"
    }]

customers_data = [
    {
        "_id": "65e88a72295cd162063ed4dc",
        "first_name": "Phillip",
        "last_name": "Castillo",
        "email": "phillip.castillo@gmail.com"
    }]
orac_orders = ['{"_id": "65e897d8beb1fb16c469ffe8", "customer_id": "65e88a72295cd162063ed4dc", "service": "mobile_app", "description": "Description for Order for Customer 65e88a72295cd162063ed4dc", "status": "orderAccepted", "update_history": [{"new_status": "orderAccepted", "when": "2024-02-14T18:04:52", "by": "65e88a72295cd162063ed540", "comment": ""}], "created": "2024-02-14T02:58:28"}']

qgen_q, qval_q, qcan_q = generate_quotation_for_accepted_orders(
    employees_data, orac_orders)




print(f"QGEN {qgen_q}")
print(f"QVAL {qval_q}")
print(f"QCAN {qcan_q}")

qval_q = generate_customer_action_on_quotations(qval_q)

print(f"QREJ OR QACC: {qval_q}")
"""
