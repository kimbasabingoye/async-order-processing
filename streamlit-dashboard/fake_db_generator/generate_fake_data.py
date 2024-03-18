import random
from datetime import datetime, timedelta
from bson import ObjectId
from faker import Faker
from enum import Enum
import json

from generate_customer_employee import generate_customer, generate_employee

from generate_orders import generate_order
from generate_quotations import generate_quotation_for_accepted_orders, generate_customer_action_on_quotations
from utils import OrderStatus, random_date, db

NUM_CUSTOMER = 10000
NUM_EMPLOYEE = 50

# Generate a large number of customers
customers_data = generate_customer(NUM_CUSTOMER)
customer_file_path = "customers.json"
with open(customer_file_path, "w") as customer_file:
    json.dump(customers_data, customer_file, indent=4)

# Generate a large number of employees
employees_data = generate_employee(NUM_EMPLOYEE)
employee_file_path = "employees.json"
with open(employee_file_path, "w") as employee_file:
    json.dump(employees_data, employee_file, indent=4)
print(type(employees_data[0]))
# Generate a large number of order
orca_orders, orej_orders, urev_orders, orac_orders = generate_order(
    customers_data, employees_data)

# print(f"Order type: {type(orac_orders)}")
orders_data = orca_orders + orej_orders + urev_orders + orac_orders
# print(orders_data)
# print(orca_orders, orej_orders, urev_orders, orac_orders)
#order_file_path = "orders.json"
#with open(order_file_path, "w") as quotation_file:
#    json.dump(orders_data, quotation_file, indent=4)
# print("Orders: ", type(orders_data[0]))
# Generate quotation for accepted order
# QGEN, QVAL, QREJ
qgen_q, qval_q, qcan_q = generate_quotation_for_accepted_orders(
    employees_data, orac_orders)

# Generate customer action on qval_q quotation
# new status will be either QACC or QREJ
qval_q = generate_customer_action_on_quotations(qval_q)

# print(qval_q)
# print(f"QVAL type: {type(qval_q)}")
quotations_data = qgen_q + qval_q + qcan_q
# print(quotations_data)
#quotation_file_path = "quotations.json"
#with open(quotation_file_path, "w") as quotation_file:
#    json.dump(quotations_data, quotation_file, indent=4)


# Insert data into MongoDB collections
employees_collection = db['employees']
customers_collection = db['customers']
quotations_collection = db["quotations"]
orders_collection = db["orders"]
realisation_collection = db["realisations"]

# Insert employee data into MongoDB collection
employees_collection.insert_many(employees_data)
print("Employee data inserted into MongoDB.")

# Insert customer data into MongoDB collection
customers_collection.insert_many(customers_data)
print("Customer data inserted into MongoDB.")

orders_collection.insert_many(orders_data)
print("Order data inserted into MongoDB.")

quotations_collection.insert_many(quotations_data)
print("Quotation data inserted into MongoDB.")

# Close MongoDB connection
db.client.close()
