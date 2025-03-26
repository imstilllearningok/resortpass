import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Pricing Tool")
st.title("Pricing Analytics Tool")
st.write("This is a tool for gyms joining BootcampPass to help them price their passes.")

st.line_chart({"Standard": [10, 15, 20, 25, 30],
               "Express": [20, 25, 30, 35, 40]})

key_path = 'C:/Users/rrichardson/Downloads/Randolph Richardson/resortpass-44c86fc588c0.json'
credentials = service_account.Credentials.from_service_account_file(key_path)

with st.sidebar:
    st.title("Inputs")

    selected_model = st.radio("Select A Model", ("X", "Y"))

    estimated_sales = st.selectbox("What is your estimated daily sales?", [50, 100, 150, 200])

    target_margin = st.selectbox("Target Profit Margin:", ["10%", "20%", "30%", "40%"])

    market = st.selectbox("Market:", ["NYC", "LA", "Chicago", "Miami"])

    sauna = st.selectbox("Sauna:", ["Yes", "No"])

load_data = st.button("Run Model")

if load_data:
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset_id = f"{credentials.project_id}.raw"
    
    dataframes = {}
    for table in client.list_tables(dataset_id):
        table_id = f"{dataset_id}.{table.table_id}"
        df = client.query(f"SELECT * FROM `{table_id}`").to_dataframe()
        dataframes[table.table_id] = df

    st.success("Data loaded from BigQuery!")

    if 'main_inventory_data' in dataframes:
        st.subheader("Main Inventory Data Preview")
        st.dataframe(dataframes['main_inventory_data'].head())
    else:
        st.warning("'main_inventory_data' not found in dataset.")

if st.button("Run Model"):
    st.write("Model is running with the following parameters:")
    st.write(f"Model: {selected_model}")
    st.write(f"Estimated Sales: {estimated_sales}")
    st.write(f"Target Margin: {target_margin}")
    st.write(f"Market: {market}")
    st.write(f"Sauna: {sauna}")



import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import cross_val_score


def catboost():

    df = client.query(f"SELECT * FROM `{table_id}`").to_dataframe()

    cat_features = [col for col in X.columns if X[col].dtype == 'object']
    X['Electrical'] = X['Electrical'].fillna(X['Electrical'].mode()[0])
    X[cat_features] = X[cat_features].fillna('Missing')
 
