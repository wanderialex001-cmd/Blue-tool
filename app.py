import streamlit as st
import websocket
import json
import pandas as pd
import threading
import time

st.set_page_config(page_title="Blue-Tool Deriv", layout="wide")
st.title("📊 Blue-Tool: Deriv Synthetic Indices Analyzer")

# Initialize session state to store historical price data
if "price_history" not in st.session_state:
    st.session_state.price_history = []

# Sidebar options
asset_dict = {
    "Volatility 75 Index": "R_75",
    "Volatility 100 Index": "R_100",
    "Boom 1000 Index": "BOOM1000",
    "Crash 500 Index": "CRASH500"
}
selected_display = st.sidebar.selectbox("Select Synthetic Index", list(asset_dict.keys()))
symbol = asset_dict[selected_display]

ma_period = st.sidebar.slider("Moving Average Period", min_value=5, max_value=50, value=14)

# WebSocket Functions
def on_message(ws, message):
    data = json.loads(message)
    if "tick" in data:
        price = data["tick"]["quote"]
        st.session_state.price_history.append(price)
        # Keep the last 100 entries to avoid filling up memory
        if len(st.session_state.price_history) > 100:
            st.session_state.price_history.pop(0)

def run_ws():
    ws = websocket.WebSocketApp(
        "wss://://derivws.com",
        on_open=lambda ws: ws.send(json.dumps({"ticks": symbol})),
        on_message=on_message
    )
    ws.run_forever()

# Start background data stream thread if not already running
if "ws_thread" not in st.session_state:
    st.session_state.ws_thread = threading.Thread(target=run_ws, daemon=True)
    st.session_state.ws_thread.start()

# Main App Layout UI
col1, col2 = st.columns([1, 3])

with col1:
    st.metric(label="Latest Live Price", value=st.session_state.price_history[-1] if st.session_state.price_history else "Connecting...")
    
    # Simple Technical Analysis
    if len(st.session_state.price_history) >= ma_period:
        df = pd.DataFrame(st.session_state.price_history, columns=["Price"])
        df["MA"] = df["Price"].rolling(window=ma_period).mean()
        
        current_ma = df["MA"].iloc[-1]
        st.metric(label=f"{ma_period}-Period MA", value=f"{current_ma:.4f}")
        
        # Simple trend signal
        if df["Price"].iloc[-1] > current_ma:
            st.success("🟢 Bullish Trend (Above MA)")
        else:
            st.error("🔴 Bearish Trend (Below MA)")
    else:
        st.warning("Gathering market ticks for indicators...")

with col2:
    if st.session_state.price_history:
        st.line_chart(st.session_state.price_history)
    else:
        st.info("Waiting for tick data stream from Deriv...")

# Automatically refresh the browser view every 2 seconds to show live movement
time.sleep(2)
st.rerun()
