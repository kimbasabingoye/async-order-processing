import streamlit as st
import altair as alt
import pandas as pd
from pymongo import UpdateOne
from bson import ObjectId
from collections import defaultdict
from pymongo import MongoClient
from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson.son import SON

client = MongoClient("mongodb://mongoadmin:secret@localhost:27017/")

db = client.get_database("TestAsyncOrderProcDB")

customers_collection = db["customers"]
employees_collection = db["employees"]
orders_collection = db["orders"]
quotation_collection = db["quotations"]
realisation_collection = db["realisations"]


class OrderStatus(str, Enum):
    UREV = 'underReview'            # OrderService
    ORAC = 'orderAccepted'          # OrderService
    OREJ = 'orderRejected'          # OrderService
    ORCA = 'orderCancelled'         # OrderService
    RESC = 'realisationScheduled'   # OrderService
    DONE = 'delivered'              # OrderService


class QuotationStatus(str, Enum):
    """Quotation status changes."""
    QGEN = 'quotationGenerated'     # QuotationService
    QVAL = 'quotationValidated'     # QuotationService
    QCAN = 'quotationCancelled'     # QuotationService
    QREJ = 'quotationRejected'      # QuotationService
    QACC = 'quotationAccepted'      # QuotationService


class RealisationStatus(str, Enum):
    RSCH = 'realisationScheduled'     # RealisationService
    RSTA = 'realisationStarted'         # RealisationService
    RCOM = 'realisationCompleted'       # RealisationService


def top_employees(n: int):
    employee_involvement = defaultdict(int)

    # Count involvement in order processing
    orders = orders_collection.find({})
    for order in orders:
        if order["update_history"]:
            for update in order["update_history"]:
                if update["new_status"] != OrderStatus.ORCA:  # Done by customer
                    employee_id = update["by"]
                    employee_involvement[employee_id] += 1

    # Count involvement in quotation processing
    quotations = quotation_collection.find({})
    for q in quotations:
        if q["update_history"]:
            for u in q["update_history"]:
                if u["new_status"] not in (QuotationStatus.QACC, QuotationStatus.QREJ):
                    employee_id = u["by"]
                    employee_involvement[employee_id] += 1

    # Count involvement in realisation processing
    realisations = realisation_collection.find({})
    for r in realisations:
        employee_id = r["employee_id"]
        employee_involvement[employee_id] += 1

    # Sort the dictionary by values in descending order
    sorted_employee_involvement = sorted(
        employee_involvement.items(), key=lambda x: x[1], reverse=True)

    # Get employee names based on their IDs
    top_employees_id = sorted_employee_involvement[:n]

    top_employees_with_names = []
    for employee_id, count in top_employees_id:
        employee = employees_collection.find_one({"_id": employee_id})
        if employee:
            top_employees_with_names.append(
                {"Name": employee["first_name"] + " " + employee["last_name"],
                 "Score": count})
        else:
            # Handle cases where employee is not found
            pass

    # Convert to DataFrame
    df = pd.DataFrame(top_employees_with_names)
    return df


def top_customers(n: int):
    top_customers_id = defaultdict(int)

    quotations = quotation_collection.find({"status": QuotationStatus.QACC})
    for q in quotations:
        order_id = q["order_id"]
        order = orders_collection.find_one({"_id": order_id})
        customer_id = order["customer_id"]

        top_customers_id[customer_id] += q["price"]

    top_customers_id = sorted(top_customers_id.items(),
                              key=lambda x: x[1], reverse=True)[:n]

    top_customers_with_names = []
    for c_id, amount in top_customers_id:
        customer = customers_collection.find_one({"_id": c_id})
        if customer:
            top_customers_with_names.append(
                {"Name": customer["first_name"] + " " + customer["last_name"],
                 "Expense": amount})
        else:
            pass

    # Convert to DataFrame
    df = pd.DataFrame(top_customers_with_names)
    return df


def order_per_month():
    # Pipeline for aggregation
    pipeline = [
        {
            "$group": {
                "_id": {
                    "month": {"$month": "$created"},
                    "service": "$service"
                },
                "total_orders": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.month": 1}
        }
    ]
    # Execute the aggregation pipeline
    result = list(orders_collection.aggregate(pipeline))

    streamlit_data = {}
    for entry in result:
        month = entry["_id"]["month"]
        service = entry["_id"]["service"]
        total_orders = entry["total_orders"]

        if month not in streamlit_data:
            streamlit_data[month] = {}

        streamlit_data[month][service] = total_orders
    return streamlit_data


def order_count_by_status():
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(orders_collection.aggregate(pipeline))
    order_count = {status["_id"]: status["count"] for status in result}
    return order_count


def order_count_by_service():
    pipeline = [
        {"$group": {"_id": "$service", "count": {"$sum": 1}}}
    ]
    result = list(orders_collection.aggregate(pipeline))
    order_count = {status["_id"]: status["count"] for status in result}
    return order_count


def quotation_count_by_status():
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(quotation_collection.aggregate(pipeline))
    quotation_count = {status["_id"]: status["count"] for status in result}
    return quotation_count


def realisation_count_by_status():
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(realisation_collection.aggregate(pipeline))
    realisation_count = {status["_id"]: status["count"] for status in result}
    return realisation_count


def realisations_completed_per_month():
    pipeline = [
        {"$lookup": {
            "from": "orders",  # Assuming orders is the name of the orders collection
            "localField": "order_id",
            "foreignField": "_id",
            "as": "order"
        }},
        {"$unwind": "$order"},  # Unwind the order array
        # Match only orders with status DONE
        {"$match": {"status": RealisationStatus.RCOM}},
        {"$project": {
            "month": {"$month": "$end_date"}
        }},
        {"$group": {
            "_id": {"month": "$month"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.month": 1}}
    ]

    # Execute the aggregation
    result = list(realisation_collection.aggregate(pipeline))

    # Convert result to DataFrame
    df = pd.DataFrame(result)

    return df


def revenue_per_month_per_service():
    pipeline = [
        # Filter quotations by accepted status
        {"$match": {"status": QuotationStatus.QACC}},
        {"$lookup": {
            "from": "orders",
            "localField": "order_id",
            "foreignField": "_id",
            "as": "order"
        }},
        {"$unwind": "$order"},  # Unwind the order array
        {"$project": {
            "year": {"$year": "$created"},
            "month": {"$month": "$created"},
            "service": "$order.service",
            "price": 1
        }},
        {"$group": {
            "_id": {"month": "$month", "service": "$service"},
            "total_revenue": {"$sum": "$price"}
        }}
    ]

    result = quotation_collection.aggregate(pipeline)

    revenue_data = []
    for entry in result:
        month = entry["_id"]["month"]
        service = entry["_id"]["service"]
        total_revenue = entry["total_revenue"]
        revenue_data.append(
            {"Month": month, "Service": service, "Total Revenue": total_revenue})

    # Convert to DataFrame
    df = pd.DataFrame(revenue_data)

    return df

def alter_chart(revenue_data):
    # Create Altair chart
    chart = alt.Chart(revenue_data).mark_line().encode(
        x="Month:T",
        y="Total Revenue:Q",
        color="Service:N",
        tooltip=["Month", "Total Revenue", "Service"]
    ).properties(
        width=600,
        height=400
    ).interactive()

    # Show Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def plot_revenue_per_service(revenue_data):
    # Display metrics for each service in three columns
    st.subheader("Total Revenue by Service")
    cols = st.columns(3)
    i = 0
    for service, service_df in revenue_data.groupby("Service"):
        total_revenue = service_df["Total Revenue"].sum()

        # Calculate delta between current month and previous month
        current_month_revenue = service_df.iloc[-1]["Total Revenue"]
        previous_month_revenue = service_df.iloc[-2]["Total Revenue"]
        delta = current_month_revenue - previous_month_revenue

        # Convert delta to an accepted type
        delta_str = str(delta)
        
        # Display metric in a column
        with cols[i]:
            st.metric(label=service, value=total_revenue, delta=delta_str)
        i += 1


# Usage example:
