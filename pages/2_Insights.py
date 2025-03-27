import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.header("Insights")

# @st.cache_data(show_spinner=False)
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

data = dataframes['agg_inventory_data (final table)']


st.write("The following insights were found:")

st.markdown("")

# st.write("**1. High-Tier Chains account for a majority of the revenue passes sell at much lower rates but account for higher share revenue:")
# # product_type = data[data['year_number'] == 2024].groupby(['product_type','year_number'])['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
# product_type = data[data['year_number'] == 2024].groupby(['product_type','year_number']).agg({'revenue':'sum','booking_rate':'mean'}).reset_index().sort_values('revenue', ascending=False)
# product_type = data[data['year_number'] == 2024].groupby(['product_type','year_number'])[['available_units','vacant_units','sold_units']].sum().reset_index()
# product_type['occupancy_rate'] = ((product_type['sold_units'] / product_type['available_units']) * 100).round(2)
# # gym_sales['occupancy_rate'] = ((gym_sales['sold_units'] / gym_sales['available_units']) * 100).round(2)

# product_type = data[data['year_number'] == 2024].groupby(['tier','product_type','has_sauna']).agg({'price':'mean','booking_rate':'mean','revenue':'sum'}).reset_index()

# st.subheader("💡 Price vs. Booking Rate (Bubble size = Revenue)")
# fig_scatter = px.scatter(
#     product_type,
#     x="price",
#     y="booking_rate",
#     size="revenue",
#     color="tier",
#     symbol="has_sauna",
#     hover_name="product_type",
#     title="Price vs Booking Rate by Product Type",
#     height=600
# )
# st.plotly_chart(fig_scatter, use_container_width=True)


# # st.dataframe(pivot_table_product)
# st.dataframe(product_type)


# x = "price"
# y = "market_median_price"

# chart = data[data['year_number'] == 2024].groupby(['gym_id']).agg({'price':'mean','booking_rate':'mean','revenue':sum}).reset_index()

# st.scatter_chart(
#     chart,
#     x="price",
#     y="booking_rate",
#     color="gym_id",
#     size='revenue'
   
# )



st.write("**1. As expected, Saturday & Sunday drive the highest amount of revenue:**")
data2 = dataframes['agg_inventory_data (final table)']
peak_day = data2.groupby(['day_of_week_name','year_number'])['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
peak_day = data2.groupby(['day_of_week_name','year_number']).agg({'revenue':'sum','booking_rate':'mean'}).reset_index().sort_values('revenue', ascending=False)
pivot_table_peak_day = pd.pivot_table(
        peak_day,
        values='revenue',
        index='day_of_week_name',
        columns='year_number',
        aggfunc='sum',
        fill_value=0
    )
pivot_table_peak_day['total'] = pivot_table_peak_day.sum(axis=1)
pivot_table_peak_day = pivot_table_peak_day.sort_values('total', ascending=False)
st.write("Total revenue by day of the week:")
st.dataframe(pivot_table_peak_day)


weekly_day_sales = data2.groupby(['week_start_date', 'day_of_week_name'])['revenue'].sum().reset_index()
average_by_day = weekly_day_sales.groupby('day_of_week_name')['revenue'].mean().round(0).reset_index().sort_values('revenue', ascending=False).reset_index()
st.write("Average revenue by day of the week:")
st.dataframe(average_by_day)


st.markdown("")


st.write("**2. In 2024, only 6 gyms sold over 60% of their available passes:**")


gym_sales = data[data['year_number'] == 2024].groupby(['gym_id','market','tier'])[['available_units','vacant_units','sold_units']].sum().reset_index()
gym_sales['occupancy_rate'] = ((gym_sales['sold_units'] / gym_sales['available_units']) * 100).round(2)
st.dataframe(gym_sales[gym_sales['occupancy_rate'] > 60].reset_index().sort_values('occupancy_rate', ascending=False).reset_index())

bins = [0, 20, 40, 60, 80, 100]
labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
gym_sales['occupancy_bin'] = pd.cut(gym_sales['occupancy_rate'], bins=bins, labels=labels, include_lowest=True)
bin_counts = gym_sales['occupancy_bin'].value_counts().sort_index()
st.dataframe(bin_counts)




low_occupancy = gym_sales[gym_sales['occupancy_rate'] <= 20]
smaller_bins = [0, 5, 10, 15, 20]
labels_smaller = ['0-5%', '6-10%', '11-15%', '16-20%']
low_occupancy['occupancy_bin'] = pd.cut(low_occupancy['occupancy_rate'], bins=smaller_bins, labels=labels_smaller, include_lowest=True)
low_bin_counts = low_occupancy['occupancy_bin'].value_counts().sort_index()



plt.figure(figsize=(5, 3))
low_bin_counts.plot(kind='bar')
plt.title('Low Occupancy Rate Distribution (0–20%) – 2024',fontsize=7)
plt.xlabel('Occupancy Rate Bins',fontsize=6)
plt.ylabel('Number of Gyms',fontsize=6)
plt.xticks(rotation=45, ha='right',fontsize=6)  
plt.yticks(fontsize=6)  
plt.tight_layout()
st.pyplot(plt)
st.markdown("")


st.write("**3. The Los Angeles market seems to have the healthiest pricing strategy - as average prices increases, demand is consistent:**")
grouped = data[data['year_number'] == 2024].groupby(['week_start_date', 'market']).agg({
    'price': 'mean',
    'booking_rate': 'mean'
}).reset_index()

correlation_by_market = (
    grouped
    .groupby('market')
    .apply(lambda df: df[['price', 'booking_rate']].corr().iloc[0, 1])
    .reset_index()
)

correlation_by_market.columns = ['market', 'weekly_corr']

correlation_df = correlation_by_market.set_index('market').T.reset_index(drop=True)

st.write("Correlation between Average Price per Pass and Occupancy Rate by Market:")
st.dataframe(correlation_df)

markets = grouped['market'].unique()

for market in markets:
    market_data = grouped[grouped['market'] == market].sort_values('week_start_date')

    fig, ax1 = plt.subplots(figsize=(6, 3))

    ax1.plot(market_data['week_start_date'], market_data['price'], color='tab:blue', label='Average Price per Pass')
    ax1.set_xlabel('Week',fontsize=6)
    ax1.set_ylabel('Average Price per Pass', color='tab:blue',fontsize=6)
    ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=6)

    ax2 = ax1.twinx()
    ax2.plot(market_data['week_start_date'], market_data['booking_rate'], color='tab:orange', label='Occupancy Rate')
    ax2.set_ylabel('Occupancy Rate (%)', color='tab:orange',fontsize=6)
    ax2.tick_params(axis='y', labelcolor='tab:orange',labelsize=6)

    ax1.tick_params(axis='x', labelsize=6)
    plt.setp(ax1.get_xticklabels(), rotation=90, ha='right')

    plt.title(f"{market} — Average Pass Price vs. Occupancy Rate by Week",fontsize=7)
    fig.tight_layout()
    st.pyplot(fig)

if st.button("Let me see the Pricing Model!"):
        st.switch_page("pages/3_Pricing Model.py")
