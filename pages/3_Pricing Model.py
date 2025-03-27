import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor, plot_importance
import matplotlib.pyplot as plt
import os


st.set_page_config(page_title="Pricing Tool")
st.title("Pricing Tool")
st.write("Please select the inputs and run the Pricing Recommendation!")

@st.cache_data(show_spinner=False)
def load_csv_data():
    filenames = ['gym_details', 'inventory_data', 'joined', 'agg_inventory_data']
    dfs = {}
    for file in filenames:
        name = file
        path = os.path.join('uploaded_data', file + '.csv')
        dfs[name] = pd.read_csv(path)
    return dfs

dataframes = load_csv_data()

dataset_options = list(dataframes.keys())

data = dataframes.get('agg_inventory_data')

with st.sidebar:
    st.title("Inputs")

    market = st.selectbox("Market:", data['market'].unique())
    product_type = st.selectbox("Product Type:", data['product_type'].unique())
    tier = st.selectbox("Tier:", data['tier'].unique())
    sauna = st.selectbox("Sauna:", data['has_sauna'].unique())
    # vacant_units = st.slider("Vacant Units", 0, 50, 10)
    # month = st.slider("Month", 1, 12, 6)
    # day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 2)
    # is_weekend = 1 if day_of_week in [5, 6] else 0

    if st.button("Get Price Recommendation"):
        st.session_state.run_model = True

if st.session_state.get('run_model', False):
    st.subheader("Model Output")

    # inventory_data = st.session_state.dataframes.get('inventory_data')
    # gym_details = st.session_state.dataframes.get('gym_details')

    # if inventory_data is None or gym_details is None:
    #     st.error("Missing required datasets: 'inventory_data' or 'gym_details'")
    #     st.stop()

    # df = inventory_data.merge(gym_details, on='gym_id')
    # df['inventory_date'] = pd.to_datetime(df['inventory_date'])
    # df['month'] = df['inventory_date'].dt.month
    # df['day_of_week'] = df['inventory_date'].dt.dayofweek
    # df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    # df['revenue'] = df['price'] * df['sold_units']
    # df['has_sauna'] = df['has_sauna'].astype(str)

    df = data.copy()

    features = ['price', 'product_type', 'tier', 'market', 'has_sauna',
                'month', 'day_of_week', 'is_weekend', 'vacant_units']
    
    target = 'revenue'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    encoders = {}
    for col in ['product_type', 'tier', 'market', 'has_sauna']:
        le = LabelEncoder()
        X_train[col] = le.fit_transform(X_train[col])
        X_test[col] = le.transform(X_test[col])
        encoders[col] = le

    model = XGBRegressor(random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    st.write(f"📉 RMSE: **{np.sqrt(mean_squared_error(y_test, preds)):.2f}**")

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_importance(model, ax=ax)
    st.pyplot(fig)

    base_features = {
        'product_type': product_type,
        'tier': tier,
        'market': market,
        'has_sauna': 'Yes' if sauna == 'Yes' else 'No',
        'month': month,
        # 'day_of_week': day_of_week,
        # 'is_weekend': is_weekend,
        # 'vacant_units': vacant_units
    }

    price_range = list(range(10, 51))
    simulation_df = pd.DataFrame([{**base_features, 'price': p} for p in price_range])
    simulation_df = simulation_df[features]

    for col, le in encoders.items():
        simulation_df[col] = le.transform(simulation_df[col])

    prediction = model.predict(simulation_df)
    optimal_idx = np.argmax(prediction)
    optimal_price = price_range[optimal_idx]
    expected_revenue = prediction[optimal_idx]

    st.success(f"💰 Optimal Price: **${optimal_price}**")
    st.info(f"📈 Expected Revenue at Optimal Price: **${expected_revenue:.2f}**")

    st.line_chart(pd.DataFrame({
        'Price': price_range,
        'Expected Revenue': prediction
    }).set_index('Price'))












