import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Exploratory Data Analysis")
st.title("Exploration")


@st.cache_data(show_spinner=False)
def load_csv_data():
    filenames = {
        'agg_inventory_data (final table)': 'agg_inventory_data',
        'gym_details (raw)': 'gym_details',
        'inventory_data (raw)': 'inventory_data', 
        'joined (raw tables joined)': 'joined'
    }
    dfs = {}
    for name, file in filenames.items():
        path = os.path.join('uploaded_data', file + '.csv')
        dfs[name] = pd.read_csv(path)
    return dfs

dataframes = load_csv_data()

dataset_options = list(dataframes.keys())  
selected_dataset = st.radio("Select Table:", dataset_options)

selected_df = dataframes[selected_dataset]

df = dataframes[selected_dataset]

tab1, tab2, tab3, tab4, tab5  = st.tabs([
    "Preview Data", "Data Information", "Describe", "Table Builder", "Visualize"
])


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
"Inventory Date": "inventory_date",
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

with tab1:
    st.dataframe(df.head())

with tab2:
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.markdown(f"```{s}```")

with tab3:
    st.dataframe(df.describe())

with tab4:

    display_names = list(categorical_col_map.keys())
    col_map = categorical_col_map

    selected_rows_display = st.multiselect("Rows (group by)", display_names)
    row_cols = [col_map[name] for name in selected_rows_display]

    selected_col_display = st.selectbox("Columns (optional, for pivot)", [None] + display_names)
    col_col = col_map[selected_col_display] if selected_col_display else None

    selected_metric = st.selectbox("Values (numerical)", numerical_cols)

    agg_func = st.selectbox("Aggregation", ["Sum", "Mean", "Count"])

    if row_cols and selected_metric:
        if agg_func == "Sum":
            aggfunc = "sum"
        elif agg_func == "Mean":
            aggfunc = "mean"
        else:
            aggfunc = "count"

        pivot_table = pd.pivot_table(
            df,
            values=selected_metric,
            index=row_cols,
            columns=col_col,
            aggfunc=aggfunc,
            fill_value=0
        )

        st.dataframe(pivot_table)

with tab5:
    if selected_dataset == "agg_inventory_data (final table)":
        
        display_names = list(categorical_col_map.keys())
        display_names_line = list(col_map_line_chart.keys())

        chart_type = st.selectbox("Chart Type", ["Line Chart", "Histogram", "Bar Chart"])

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
            selected_display = st.selectbox("Group By:", [None] + display_names_line)
            selected_metric = st.selectbox("Metric:", numerical_cols)
            selected_aggregation = st.selectbox("Aggregation:", ["Sum", "Mean", "Count"])
            group_by = col_map_line_chart.get(selected_display) if selected_display else None

            if group_by:
                data = df.groupby(["inventory_date", group_by])[selected_metric].sum().unstack()
            else:
                data = df.groupby("inventory_date")["sold_adult_units"].sum()

            st.line_chart(data)

        # elif chart_type == "Scatter Plot":
        #     x = st.selectbox("X axis", numerical_cols)
        #     y = st.selectbox("Y axis", [col for col in numerical_cols if col != x])
        #     st.write(f"Scatter Plot: {x} vs {y}")
        #     st.scatter_chart(df[[x, y]])
    else:
        st.write("Please select 'agg_inventory_data' table to visualize data.") 