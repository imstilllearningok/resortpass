import streamlit as st


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


st.header("Insights")
st.write("Based on the data exploration, the following insights were found:")
data = dataframes['agg_inventory_data (final table)']
peak_day = data.groupby('day_of_week_name')['sold_adult_units'].sum().idxmax()
peak_month = data.groupby('month_name')['sold_adult_units'].sum().idxmax()
top_market = data.groupby('market')['revenue'].sum().idxmax()
st.dataframe(data.head(5))



group = data.groupby(['inventory_date','market'])['sold_adult_units'].sum().reset_index()
st.dataframe(group)

average_daily_sales = group['sold_adult_units'].mean()
st.metric("Average Daily Sold Passes", average_daily_sales)
st.dataframe(data.groupby(['gym_id','market'])['revenue'].sum().sort_values(ascending=False).reset_index().head(5))
top_gym = data.groupby('gym_id')['revenue'].sum().idxmax()
top_product = data.groupby('product_id')['revenue'].sum().idxmax()
st.write(f"The peak day for sales is {peak_day}.")
st.write(f"The peak month for sales is {peak_month}.")
st.write(f"The top market by revenue is {top_market}.")
st.write(f"The top gym by revenue is {top_gym}.")
st.write(f"The top product by revenue is {top_product}.")



st.write("New York City sees much higher peaks during the summer months:")
st.line_chart(data.groupby(["inventory_date", group_by])[selected_metric].sum().unstack())

st.dataframe(data.groupby(['month_name','market'])['sold_adult_units'].sum().reset_index())