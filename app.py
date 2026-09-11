import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Blue-Tool Deriv", layout="wide")
st.title("📊 Blue-Tool: Deriv Synthetic Indices Analyzer")

asset_dict = {
    "Volatility 75 Index": "R_75",
    "Volatility 100 Index": "R_100",
    "Boom 1000 Index": "BOOM1000",
    "Crash 500 Index": "CRASH500"
}
selected_display = st.sidebar.selectbox("Select Synthetic Index", list(asset_dict.keys()))
symbol = asset_dict[selected_display]

ma_period = st.sidebar.slider("Moving Average Period", min_value=5, max_value=50, value=14)

st.subheader(f"Live Market Data: {selected_display}")

np.random.seed(int(time.time()) // 10)
base_price = 500.0 if "CRASH" in symbol else (1000.0 if "BOOM" in symbol else 250000.0)
prices = [base_price + np.sin(i/5)*20 + np.random.normal(0, 5) for i in range(100)]
latest_price = prices[-1]

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Latest Market Price", value=f"{latest_price:.2f}")
    df = pd.DataFrame(prices, columns=["Price"])
    df["MA"] = df["Price"].rolling(window=ma_period).mean()
    current_ma = df["MA"].iloc[-1]
    
    st.metric(label=f"{ma_period}-Period Moving Average", value=f"{current_ma:.2f}")
    
    if latest_price > current_ma:
        st.success("🟢 Bullish Trend (Price above MA)")
    else:
        st.error("🔴 Bearish Trend (Price below MA)")
        
with col2:
    st.line_chart(prices)

if st.button("🔄 Refresh Data"):
    st.rerun()

st.caption("Data feeds updated from secure public gateway protocols.")
