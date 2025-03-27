import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account
import os

st.set_page_config(page_title="Homepage")
st.markdown("""
    <style>
        div.block-container {
            padding-top: 3rem;
        }
        h1 {
            margin-bottom: 0.25rem;
        }
    </style>
""", unsafe_allow_html=True)
st.header("Analytics Engineering Assessment")


st.markdown("**By: Randolph Richardson**")


st.markdown("")


st.markdown("**Tools:**")
lst = ['Streamlit - web application', 
       'Google Cloud Platform (BigQuery) - data warehouse',
       'dbt - data cleaning and transformations',
       'Python (various packages) - data analysis, visualization, and pricing model development',
       'GitHub - version control']
s = ''

for i in lst:
    s += "- " + i + "\n"

st.markdown(s)



st.markdown("")
st.markdown("")



st.markdown("All data already exists in BigQuery & dbt, but below is an example of how this tool can be expanded for different data sources. Feel free to skip to the 'Exploration' page.")

    
# key_path = st.secrets["gcp_service_account"]["gcp_service_account"]
# st.write(key_path)
# credentials = service_account.Credentials.from_service_account_file(key_path)
# client = bigquery.Client(credentials=credentials, project=credentials.project_id)




def start_of_assessment():

    if "start_clicked" not in st.session_state:
        st.session_state.start_clicked = False

    if "bootcamp_data_uploaded" not in st.session_state:
        st.session_state.bootcamp_data_uploaded = False 

    if st.button("**Upload Data!**"):
        st.session_state.start_clicked = True

    if st.button("Skip to Exploration"):
        st.switch_page("pages/1_Exploration.py")

    if st.session_state.start_clicked:
        row_input = st.columns((2,1,2,1))
        with row_input[0]:
            data_source = st.selectbox("Select Data Source:", ["BootcampPass", "Upload Your Own Data"])

        csv_data = {}
        selected_sheets = []

        if data_source == "BootcampPass":
            # if st.button("Upload BootcampPass Data"):
            #     st.session_state.bootcamp_data_uploaded = True

            if st.button("Upload BootcampPass Data"):
                
                available_files = {
                    "BootcampPass": "uploaded_data/Analytics Engineering  Case Study Data External Version.xlsx"
                }

                list_of_sheets = list(available_files.keys())
                selected_path = available_files[list_of_sheets[0]]

                excel_data = pd.ExcelFile(selected_path)
                for sheet_name in excel_data.sheet_names:
                    sheet_data = pd.read_excel(excel_data, sheet_name=sheet_name)
                    csv_data[sheet_name] = sheet_data
                    with st.expander(f"Preview Data: {sheet_name}"):
                        st.dataframe(sheet_data)
                
                st.success("Data uploaded successfully!")

                # selected_sheets = st.multiselect("Select Sheets to Upload to BigQuery:", excel_data.sheet_names)

        elif data_source == "Upload Your Own Data":
            st.session_state.bootcamp_data_uploaded = False 
            row_input = st.columns((2,1,2,1))
            with row_input[0]:
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

                    # selected_sheets = st.multiselect("Select Sheets to Upload to BigQuery:", excel_data.sheet_names)
                    st.success("Data uploaded successfully!")
                elif file_type == ".csv":
                    df = pd.read_csv(uploaded_file)
                    csv_data["Uploaded_CSV"] = df
                    st.dataframe(df)
                    selected_sheets = ["Uploaded_CSV"]
                    st.success("Data uploaded successfully!")


        def insert_data():
            key_path = st.secrets["gcp_service_account"]['gcp_service_account']
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

                st.success(f"Loaded {sheet_name} into BigQuery table {table_id}")

        if selected_sheets:
            add = st.button("Add Selected Data to BigQuery")
            if add:
                st.success("Data added to BigQuery!")

        

start_of_assessment()


