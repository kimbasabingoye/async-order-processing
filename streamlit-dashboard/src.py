from utils import top_employees, top_customers, order_count_by_status, order_count_by_service, quotation_count_by_status, realisations_completed_per_month, revenue_per_month_per_service, realisation_count_by_status, order_per_month

# Example usage:
top_employees = top_employees(10)
top_customers = top_customers(10)
total_order_per_status = order_count_by_status()
total_order_per_service = order_count_by_service()
t_order_per_month = order_per_month()

total_quotation_per_status = quotation_count_by_status()

realisations_count = realisations_completed_per_month()
total_realisation_per_status = realisation_count_by_status()
total_revenue_per_service = revenue_per_month_per_service()


"""

print(f"TOP Employees: {top_employees}")

print(f"TOP Customers: {top_customers}")

print(f"TOTAL order per status: {total_order_per_status}")
print(f"TOTAL order per service: {total_order_per_service}")
print(f"TOTAL order per month: {t_order_per_month}")

print(f"TOTAL quotation per status: {total_quotation_per_status}")
"""
print(f"TOTAL realisation Completed per month: {realisations_count}")
#print(f"TOTAL realisation per status: {total_realisation_per_status}")


#print(f"TOTAL revenu per service: \n{total_revenue_per_service}")

