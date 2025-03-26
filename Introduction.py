import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Set Page Title & Layout
st.set_page_config(page_title="Homepage")
st.title("Analytics Engineering Assessment")
st.subheader("By Randolph Richardson")





st.markdown("Welcome! This is my submission for the Analytics Engineering Assessment for ResortPass.")
# st.markdown("I separated the assessment into three parts: Data Ingestion, Exploratator Data Analysis, Pricing Tool, and a Summary Data Analysis.")

st.markdown("**The tools I used:**")
lst = ['Streamlit - for the web application', 
       'Google Cloud Platform (BigQuery) - for the data warehouse',
       'DBT - for data transformation',
       'Python (various packages) - for data manipulation, analysis, visualization, and modeling']
s = ''

for i in lst:
    s += "- " + i + "\n"

st.markdown(s)


def start_of_assessment():

    if "start_clicked" not in st.session_state:
        st.session_state.start_clicked = False

    if "bootcamp_data_uploaded" not in st.session_state:
        st.session_state.bootcamp_data_uploaded = False

    if st.button("Begin!"):
        st.session_state.start_clicked = True

    if st.session_state.start_clicked:
        st.write("All of the data is already in BigQuery, but here is a simple tool to add more if needed!")
        st.write("You can explore additional upload options here (live connection to BQ, but not used in assessment.")
        st.write("Feel free to skip to 'Exploratory Data Analysis' to see the data.")

        data_source = st.radio("Select Data Source:", ["BootcampPass", "Upload Your Own Data"])

        csv_data = {}
        selected_sheets = []

        if data_source == "BootcampPass":
            if st.button("Upload BootcampPass Data"):
                st.session_state.bootcamp_data_uploaded = True

            if st.session_state.bootcamp_data_uploaded:
                
                available_files = {
                    "BootcampPass": "C:/Users/rrichardson/Documents/rp/app/data/Analytics Engineering  Case Study Data External Version.xlsx",
                }

                list_of_sheets = list(available_files.keys())
                selected_path = available_files[list_of_sheets[0]]
                file_type = "XLSX" if selected_path.endswith(".xlsx") else "CSV"

                if file_type == "XLSX":
                    excel_data = pd.ExcelFile(selected_path)
                    for sheet_name in excel_data.sheet_names:
                        sheet_data = pd.read_excel(excel_data, sheet_name=sheet_name)
                        csv_data[sheet_name] = sheet_data
                        with st.expander(f"Preview Data: {sheet_name}"):
                            st.dataframe(sheet_data)

                    selected_sheets = st.multiselect("Select Sheets to Upload to BigQuery:", excel_data.sheet_names)

                elif file_type == "CSV":
                    df = pd.read_csv(selected_path)
                    csv_data["BootcampPass_CSV"] = df
                    st.dataframe(df)
                    selected_sheets = ["BootcampPass_CSV"]

        elif data_source == "Upload Your Own Data":
            st.session_state.bootcamp_data_uploaded = False  # Reset in case of switching sources
            file_type = st.selectbox("Select File Type:", [".csv", ".xlsx"])
            uploaded_file = st.file_uploader("Upload Your File:", type=["csv", "xlsx"])

            if uploaded_file:
                if file_type == ".xlsx":
                    excel_data = pd.ExcelFile(uploaded_file)
                    for sheet_name in excel_data.sheet_names:
                        sheet_data = pd.read_excel(excel_data, sheet_name=sheet_name)
                        csv_data[sheet_name] = sheet_data
                        with st.expander(f"Preview Data: {sheet_name}"):
                            st.dataframe(sheet_data)

                    selected_sheets = st.multiselect("Select Sheets to Upload to BigQuery:", excel_data.sheet_names)

                elif file_type == ".csv":
                    df = pd.read_csv(uploaded_file)
                    csv_data["Uploaded_CSV"] = df
                    st.dataframe(df)
                    selected_sheets = ["Uploaded_CSV"]

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

                st.success(f"✅ Loaded `{sheet_name}` into BigQuery table `{table_id}`")

        if selected_sheets:
            st.button("Add Selected Data to BigQuery", on_click=insert_data)

start_of_assessment()