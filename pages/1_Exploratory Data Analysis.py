import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Exploratory Data Analysis")
st.title("Exploratory Data Analysis")

st.markdown(
    "CSV files are being used for analysis. These CSVs represent raw and transformed tables. "
    "Explore insights from the raw and final analysis tables below."
)

@st.cache_data(show_spinner=False)
def load_csv_data():
    filenames = ['gym_details.csv', 'inventory_data.csv', 'joined.csv', 'agg_inventory_data.csv']
    dfs = {}
    for file in filenames:
        name = file.replace('.csv', '')
        path = os.path.join(file)
        dfs[name] = pd.read_csv(path)
    return dfs

dataframes = load_csv_data()

dataset_options = list(dataframes.keys())
selected_dataset = st.radio("Select Table:", dataset_options)

df = dataframes[selected_dataset]

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

    if chart_type == "Histogram" and num_cols:
        col = st.selectbox("Column", num_cols)
        st.bar_chart(df[col].value_counts())

    elif chart_type == "Bar Chart" and cat_cols and num_cols:
        x_col = st.selectbox("X (categorical)", cat_cols)
        y_col = st.selectbox("Y (numerical)", num_cols)
        st.bar_chart(df.groupby(x_col)[y_col].mean().sort_values(ascending=False))

    elif chart_type == "Line Chart" and num_cols:
        x_col = st.selectbox("X axis", num_cols)
        st.line_chart(df[[x_col]])

    elif chart_type == "Scatter Plot" and len(num_cols) > 1:
        x = st.selectbox("X axis", num_cols)
        y = st.selectbox("Y axis", [col for col in num_cols if col != x])
        st.scatter_chart(df[[x, y]])
