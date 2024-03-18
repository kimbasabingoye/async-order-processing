import json
from faker import Faker
from bson import ObjectId
from utils import generate_email, db

NUM_EMPLOYEE = 500
NUM_CUSTOMER = NUM_EMPLOYEE * 20



def generate_customer(n: int):
    # Generate a large number of customers
    customers_data = []
    for i in range(n):
        # Create a Faker instance
        faker = Faker()
        # Generate a fake first name
        first_name = faker.first_name()
        # Generate a fake last name
        last_name = faker.last_name()
        email = generate_email(first_name, last_name)
        customers_data.append({
            "_id": str(ObjectId()),
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        })
    return customers_data


def generate_employee(n: int):
    # Generate a large number of employees
    employees_data = []
    for i in range(NUM_EMPLOYEE):
        # Create a Faker instance
        faker = Faker()
        # Generate a fake first name
        first_name = faker.first_name()
        # Generate a fake last name
        last_name = faker.last_name()
        email = generate_email(first_name, last_name)
        employees_data.append({
            "_id": str(ObjectId()),
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        })
    return employees_data
