import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Exploratory Data Analysis")
st.title("Exploratory Data Analysis")

st.markdown(
    "To speed up web application, CSV files are being used for this analysis. Below are the CSVs, representing raw and transformed tables:"
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
    "Preview Data", "Data Information", "Shape", "Describe", "Visualize"
])

with tab1:
    st.dataframe(df.head())

with tab2:
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.markdown(f"```{s}```")

with tab3:
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

with tab4:
    st.dataframe(df.describe())

with tab5:

    # Define columns of interest
    numerical_cols = [
        "price", "vacant_adult_units", "sold_adult_units", "available_units",
        "booking_rate", "vacancy_rate", "revenue",
        "rolling_avg_booking_rate_last_4_weeks", "rolling_avg_vacancy_rate_last_4_weeks",
        "market_median_price", "market_avg_price", "market_avg_booking_rate",
        "price_vs_market_median", "booking_rate_vs_market"
    ]

    categorical_col_map = {
    "Product ID": "product_id",
    "Gym ID": "gym_id",
    "Sauna": "has_sauna",
    "Market": "market",
    "Tier": "tier",
    "Product Type": "product_type",
    "Day of Week": "day_of_week_name",
    "Month": "month_name",
    "Weekend": "is_weekend",
    "Quarter": "quarter"
    }

    col_map_line_chart = {
    "Sauna": "has_sauna",
    "Market": "market",
    "Tier": "tier",
    "Product Type": "product_type",
    "Day of Week": "day_of_week_name",
    "Month": "month_name",
    "Weekend": "is_weekend",
    "Quarter": "quarter"
    }

    if selected_dataset == 'agg_inventory_data':

        display_names = list(categorical_col_map.keys())
        display_names_line = list(col_map_line_chart.keys())

        chart_type = st.selectbox("Chart Type", ["Line Chart", "Histogram", "Bar Chart", "Scatter Plot"])

        if chart_type == "Histogram":
            col = st.selectbox("Numerical Column", numerical_cols)
            bins = st.slider("Number of bins", 5, 100, 30)
            st.write(f"Histogram for {col}")
            st.bar_chart(df[col].value_counts(bins=bins).sort_index())

        elif chart_type == "Bar Chart":
            selected_display = st.selectbox("X (categorical)", display_names)
            x_col = categorical_col_map.get(selected_display)
            y_col = st.selectbox("Y (numerical)", numerical_cols)
            agg_func = st.selectbox("Aggregation", ["Mean", "Sum", "Count"])

            if agg_func == "Mean":
                data = df.groupby(x_col)[y_col].mean().sort_values(ascending=False)
            elif agg_func == "Sum":
                data = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
            else:
                data = df.groupby(x_col)[y_col].count().sort_values(ascending=False)

            st.bar_chart(data)

        elif chart_type == "Line Chart":
            selected_display = st.selectbox("Group By: (optional)", [None] + display_names_line)
            group_by = col_map_line_chart.get(selected_display) if selected_display else None

            if group_by:
                data = df.groupby(["inventory_date", group_by])["sold_adult_units"].sum().unstack()
            else:
                data = df.groupby("inventory_date")["sold_adult_units"].sum()

            st.line_chart(data)

        elif chart_type == "Scatter Plot":
            x = st.selectbox("X axis", numerical_cols)
            y = st.selectbox("Y axis", [col for col in numerical_cols if col != x])
            st.write(f"Scatter Plot: {x} vs {y}")
            st.scatter_chart(df[[x, y]])
    else:
        None
