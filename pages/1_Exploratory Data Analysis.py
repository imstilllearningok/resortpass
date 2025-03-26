import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Exploratory Data Analysis")
st.title("Exploratory Data Analysis")

st.markdown("Behind the scenes, raw tables were added to BigQuery. Transformation and cleaning were done using DBT. We merged the tables, added a calendar & holiday table, and created a final table for analysis. Below you can see insights into the raw table along with the final analysis table.")

key_path = 'C:/Users/rrichardson/Downloads/Randolph Richardson/resortpass-44c86fc588c0.json'

@st.cache_resource(show_spinner=False)
def load_data():
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset_id = f"{credentials.project_id}.raw"

    dfs = {}
    for table in client.list_tables(dataset_id):
        table_id = f"{dataset_id}.{table.table_id}"
        df = client.query(f"SELECT * FROM `{table_id}`").to_dataframe()
        dfs[table.table_id] = df
    return dfs

if 'dataframes' not in st.session_state:
    st.session_state.dataframes = load_data()

dataset_options = ['gym_details','inventory_details','merged_data','final_analysis']
selected_dataset = st.radio("Select Table:", dataset_options)

df = st.session_state.dataframes[selected_dataset]

# with st.sidebar:
#     st.header("Filters")
#     col_filters = {}
#     for col in df.select_dtypes(include='object').columns:
#         unique_vals = df[col].dropna().unique()
#         if len(unique_vals) <= 50:
#             selected_vals = st.multiselect(f"{col}", unique_vals, default=unique_vals)
#             col_filters[col] = selected_vals

#     for col, vals in col_filters.items():
#         df = df[df[col].isin(vals)]

#     st.header("Group By")
#     group_by_col = st.selectbox("Group by", [""] + list(df.columns))
#     agg_col = st.selectbox("Aggregate", [""] + list(df.select_dtypes(include='number').columns))
#     agg_func = st.selectbox("Aggregation Function", ["mean", "sum", "count", "max", "min"])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Preview", "Data Information", "Shape", "Descriptive Stats", "Charts"
])

with tab1:
    st.dataframe(df.head())

with tab2:
    st.subheader("Data Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

with tab3:
    st.subheader("Column and Row Count")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

with tab4:
    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe())

with tab5:
    st.subheader("Charts")
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    chart_type = st.selectbox("Chart Type", ["Histogram", "Bar Chart", "Line Chart", "Scatter Plot"])

    if chart_type == "Histogram":
        col = st.selectbox("Column", num_cols)
        st.bar_chart(df[col].value_counts())

    elif chart_type == "Bar Chart":
        x_col = st.selectbox("X (categorical)", cat_cols)
        y_col = st.selectbox("Y (numerical)", num_cols)
        st.bar_chart(df.groupby(x_col)[y_col].mean().sort_values(ascending=False))

    elif chart_type == "Line Chart":
        x_col = st.selectbox("X axis", num_cols)
        st.line_chart(df[[x_col]])

    elif chart_type == "Scatter Plot":
        x = st.selectbox("X axis", num_cols)
        y = st.selectbox("Y axis", num_cols, index=1 if len(num_cols) > 1 else 0)
        st.scatter_chart(df[[x, y]])

if group_by_col and agg_col:
    st.subheader(f"Grouped Data: {group_by_col} → {agg_func}({agg_col})")
    grouped_df = df.groupby(group_by_col)[agg_col].agg(agg_func).reset_index()
    st.dataframe(grouped_df)
