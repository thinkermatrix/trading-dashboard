# dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

st.set_page_config(page_title="Trading AI Agent", layout="wide")
st.title("🤖 Trading AI Agent Dashboard")

# ---- URL of your log file (we'll use a public sample for now) ----
LOGS_URL = "https://raw.githubusercontent.com/thinkermatrix/trading-agent-logs/main/logs.csv"
# Replace with your own when ready

@st.cache_data(ttl=30)
def load_logs():
    try:
        resp = requests.get(LOGS_URL)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except:
        return pd.DataFrame()

def main():
    st.header("📡 Live Agent Monitor")
    df = load_logs()

    if df.empty:
        st.warning("No logs found. Make sure your log file is accessible.")
        return

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    latest = df.iloc[-1]
    col1.metric("Equity", f"${latest['equity']:,.2f}")
    col2.metric("Cash", f"${latest['cash']:,.2f}")

    if len(df) > 1:
        pnl = latest['equity'] - df['equity'].iloc[0]
        col3.metric("Total P&L", f"${pnl:,.2f}")
        cummax = df['equity'].cummax()
        dd = (df['equity'] - cummax) / cummax
        col4.metric("Max Drawdown", f"{dd.min()*100:.2f}%")
    else:
        col3.metric("Total P&L", "$0.00")
        col4.metric("Max Drawdown", "0.00%")

    # --- Prediction gauge ---
    if 'prob_up' in df.columns:
        st.subheader("Latest Prediction")
        last_prob = latest['prob_up']
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=last_prob,
            title={'text': "Bullish Probability"},
            gauge={'axis': {'range': [0,1]}, 'bar': {'color': "darkblue"}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    # --- Equity curve ---
    st.subheader("Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['equity'],
                             mode='lines', name='Equity'))
    fig.update_layout(xaxis_title="Time", yaxis_title="Value ($)")
    st.plotly_chart(fig, use_container_width=True)

    # --- Log table ---
    st.subheader("Recent Log Entries")
    st.dataframe(df.tail(20), use_container_width=True)

if __name__ == "__main__":
    main()
