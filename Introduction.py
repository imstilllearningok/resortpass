import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Set Page Title & Layout
st.set_page_config(page_title="Homepage")
st.title("Analytics Engineering Assessment")

# Data source selection
data_source = st.radio("Select Data:", ["BootcampPass", "Upload Your Own Data"])

csv_data = {}
selected_sheets = []

if data_source == "BootcampPass":
    available_files = {
        "BootcampPass": "C:/Users/rrichardson/Documents/rp/app/data/Analytics Engineering  Case Study Data External Version.xlsx",
    }

    selected_given = st.selectbox("Choose A File:", list(available_files.keys()))
    selected_path = available_files[selected_given]

    file_type = "XLSX" if selected_path.endswith(".xlsx") else "CSV"

    if file_type == "XLSX":
        excel_data = pd.ExcelFile(selected_path)
        for sheet_name in excel_data.sheet_names:
            sheet_data = pd.read_excel(excel_data, sheet_name=sheet_name)
            csv_data[sheet_name] = sheet_data
            with st.expander(f"Preview Data: {sheet_name}"):
                st.dataframe(sheet_data)

        selected_sheets = st.multiselect("Select File to Upload to BigQuery:", excel_data.sheet_names)

    elif file_type == "CSV":
        df = pd.read_csv(selected_path)
        csv_data["given_csv"] = df
        st.dataframe(df)
        selected_sheets = ["given_csv"]

elif data_source == "Upload Your Own Data":
    file_type = st.selectbox("Select File Type:", [".csv", ".xlsx"])
    uploaded_file = st.file_uploader("Upload File:", type=["csv", "xlsx"])

    if uploaded_file and file_type == "XLSX":
        excel_data = pd.ExcelFile(uploaded_file)
        for sheet_name in excel_data.sheet_names:
            sheet_data = pd.read_excel(excel_data, sheet_name=sheet_name)
            csv_data[sheet_name] = sheet_data
            with st.expander(f"Preview: {sheet_name}"):
                st.dataframe(sheet_data)

        selected_sheets = st.multiselect("Select sheets to upload to BigQuery", excel_data.sheet_names)

    elif uploaded_file and file_type == "CSV":
        df = pd.read_csv(uploaded_file)
        csv_data["uploaded_csv"] = df
        st.dataframe(df)
        selected_sheets = ["uploaded_csv"]

def insert_data():
    key_path = 'C:/Users/rrichardson/Downloads/Randolph Richardson/resortpass-44c86fc588c0.json'
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    for sheet_name in selected_sheets:
        df = csv_data[sheet_name]
        table_id = f"{credentials.project_id}.raw.{sheet_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition="WRITE_TRUNCATE"
        )

        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            load_job = client.load_table_from_file(csv_buffer, table_id, job_config=job_config)
            load_job.result()

        st.success(f"Loaded {sheet_name} into BigQuery Table {table_id}")

# Upload Button
if selected_sheets:
    st.button("Add Selected Data to BigQuery", on_click=insert_data)
