import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor, plot_importance
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Pricing Model")
st.header("Pricing Model")

st.write("Select Inputs on the left and then click the button below:")

# Load data
# @st.cache_data
def load_csv_data():
    filenames = ['gym_details', 'inventory_data', 'joined', 'agg_inventory_data']
    dfs = {}
    for file in filenames:
        path = os.path.join('uploaded_data', file + '.csv')
        dfs[file] = pd.read_csv(path)
    return dfs

dataframes = load_csv_data()
data = dataframes.get('agg_inventory_data')

data['inventory_date'] = pd.to_datetime(data['inventory_date'], errors='coerce')
data['day_of_week_name'] = data['day_of_week_name']
data['month_name'] = data['month_name']
data['has_sauna'] = data['has_sauna']
data['available_units'] = data['available_units'].fillna(10)
data['revenue'] = data['price'] * data['sold_units']

with st.sidebar:
    st.title("Inputs")
    market = st.selectbox("Market", sorted(data['market'].dropna().unique()))
    product_type = st.selectbox("Product Type", sorted(data['product_type'].dropna().unique()))
    tier = st.selectbox("Tier", sorted(data['tier'].dropna().unique()))
    sauna = st.selectbox("Sauna", sorted(data['has_sauna'].dropna().unique()))
    month_name = st.selectbox("Month", sorted(data['month_name'].dropna().unique()))
    day_of_week_name = st.selectbox("Day of Week", sorted(data['day_of_week_name'].dropna().unique()))
    available_units = st.slider("Available Units", 0, 50, 10)

if st.button("**Run Model**"):
    df = data.copy()

    features = [
        'price', 'product_type', 'tier', 'market', 'has_sauna',
        'month_name', 'day_of_week_name', 'available_units'
    ]
    target = 'revenue'

    X = df[features].copy()
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    encoders = {}
    for col in ['product_type', 'tier', 'market', 'has_sauna', 'month_name', 'day_of_week_name']:
        le = LabelEncoder()
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        X_test[col] = le.transform(X_test[col].astype(str))
        encoders[col] = le

    model = XGBRegressor(random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))


    base_features = {
        'product_type': product_type,
        'tier': tier,
        'market': market,
        'has_sauna': sauna,
        'month_name': month_name,
        'day_of_week_name': day_of_week_name,
        'available_units': available_units
    }

    price_range = list(range(10, 51))
    simulation_df = pd.DataFrame([{**base_features, 'price': p} for p in price_range])
    simulation_df = simulation_df[features]

    for col, le in encoders.items():
        simulation_df[col] = le.transform(simulation_df[col].astype(str))

    prediction = model.predict(simulation_df)
    optimal_idx = np.argmax(prediction)
    optimal_price = price_range[optimal_idx]
    expected_revenue = prediction[optimal_idx]

    st.success(f"Optimal Price: **${optimal_price}**")
    st.info(f"Expected Revenue at Optimal Price: **${expected_revenue:.2f}**")

    chart_df = pd.DataFrame({
        'Price': price_range,
        'Expected Revenue': prediction
    }).set_index('Price')


    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(chart_df.index, chart_df['Expected Revenue'], color='tab:blue', label='Expected Revenue')
    ax1.set_xlabel('Price', fontsize=15)
    ax1.set_ylabel('Expected Revenue', color='tab:blue', fontsize=15)
    ax1.tick_params(axis='both', labelsize=15)
    ax1.tick_params(axis='y', labelcolor='tab:blue',labelsize=15)

    st.pyplot(fig1)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    plot_importance(model, ax=ax2)
    ax2.set_xlabel('Importance Value', fontsize=15)
    ax2.set_ylabel('Feature', color='tab:blue', fontsize=15)
    ax2.tick_params(axis='both', labelsize=15)
    ax2.set_title('Feature Importance', fontsize=15)
    ax2.grid(False)


    st.pyplot(fig2)