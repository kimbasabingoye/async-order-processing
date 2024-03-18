#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

from utils import top_customers, top_employees, revenue_per_month_per_service, plot_revenue_per_service, realisations_completed_per_month

TOP = 10

#######################
# Page configuration
st.set_page_config(
    page_title="Order Processing Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
#df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')


#######################
# Sidebar

with st.sidebar:
    st.title('🏂 Order Processing Dashboard')


#######################
# Plots


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Top Employees')
    top_employees_data = top_employees(TOP)

    st.dataframe(top_employees_data,
                 column_order=("Name", "Score"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "name": st.column_config.TextColumn(
                         "Name",
                     ),
                     "Score": st.column_config.ProgressColumn(
                         "Score",
                         format="%f",
                         min_value=0,
                         max_value=max(top_employees_data["Score"]),
                     )}
                 )

with col[1]:
    revenue_data = revenue_per_month_per_service()
    plot_revenue_per_service(revenue_data)

    df = realisations_completed_per_month()


with col[2]:
    st.markdown('#### Top Customers')
    top_customers_data = top_customers(TOP)

    st.dataframe(top_customers_data,
                 column_order=("Name", "Expense"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "name": st.column_config.TextColumn(
                         "Name",
                     ),
                     "Expense": st.column_config.ProgressColumn(
                         "Expense",
                         format="%f",
                         min_value=0,
                         max_value=max(top_customers_data["Expense"]),
                     )}
                 )
