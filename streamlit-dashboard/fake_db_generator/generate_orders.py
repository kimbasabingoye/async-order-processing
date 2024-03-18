from bson import ObjectId

from utils import OrderStatus, random_date
import random, json,sys
from datetime import datetime

order_file_path = "orders.json"
#with open(order_file_path, "w") as order_file:
#    json.dump(orders_data, order_file, indent=4)

def generate_order(customers_data, employees_data):
    """ Orders with random status between UREV, ORAC, OREJ, and ORCA

    """
    # Generate orders for each customer
    urev_orders = []
    orac_orders = []
    orca_orders = []
    orej_orders = []

    for customer in customers_data:
        num_orders = random.randint(0, 10)
        for _ in range(num_orders):
            service = random.choice(["web_site", "mobile_app", "desktop_app"])
            description = f"Description for Order for Customer {customer['_id']}"

            # Choose a random status between UREV, ORAC, OREJ, and ORCA
            status = random.choice(
                [OrderStatus.UREV, OrderStatus.ORAC, OrderStatus.OREJ, OrderStatus.ORCA])

            # Choose the updater based on the selected status
            if status in [OrderStatus.ORAC, OrderStatus.OREJ]:
                updater = random.choice(employees_data)["_id"]
            else:  # for order cancelled
                updater = customer["_id"]

            # Generate a random creation date
            created = random_date(datetime(2016, 1, 1), datetime.now())

            # Generate a random date for when.isoformat(), after the created date
            when = random_date(created, datetime.now())

            order = {
                "_id": str(ObjectId()),
                "customer_id": customer["_id"],
                "service": service,
                "description": description,
                "status": status,
                "update_history": [{
                    "new_status": status,
                    "when": when,
                    "by": updater,
                    "comment": ""
                }],
                "created": created,
            }
            #order = json.dumps(order)
            if status == OrderStatus.UREV:
                urev_orders.append(order)
            elif status == OrderStatus.OREJ:
                orej_orders.append(order)
            elif status == OrderStatus.ORCA:
                orca_orders.append(order)
            else:
                orac_orders.append(order) # Need to proceed with this 
            
    return orca_orders, orej_orders, urev_orders, orac_orders

"""
employees_data = [
    {
        "_id": "65e88a72295cd162063ed540",
        "first_name": "Dalton",
        "last_name": "Klein",
        "email": "dalton.klein@example.com"
}]

customers_data = [
    {
        "_id": "65e88a72295cd162063ed4dc",
        "first_name": "Phillip",
        "last_name": "Castillo",
        "email": "phillip.castillo@gmail.com"
}]


orca_orders, orej_orders, urev_orders, orac_orders = generate_order(
    customers_data, employees_data)

#print(orac_orders)
"""
