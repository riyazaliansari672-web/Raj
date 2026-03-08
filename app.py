import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# ऐप की सेटिंग
st.set_page_config(page_title="Rozitreding App", layout="wide")
st.title("🚀 Rozitreding: Live RSI 6 Dashboard")

# साइडबार में सेटिंग्स
st.sidebar.header("Trading Controls")
symbol = st.sidebar.selectbox("Select Coin", ["DOGE/USDT", "BTC/USDT", "ETH/USDT", "XRP/USDT"])
timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h"])

def fetch_crypto_data(symbol, tf):
    # Bybit का उपयोग ताकि मोबाइल पर एरर न आए
    exchange = ccxt.bybit()
    bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    # आपकी पसंद का RSI 6 इंडिकेटर
    df['RSI'] = ta.rsi(df['close'], length=6)
    return df

try:
    data = fetch_crypto_data(symbol, timeframe)
    last_rsi = data['RSI'].iloc[-1]
    last_price = data['close'].iloc[-1]

    # मुख्य स्क्रीन पर डेटा दिखाना
    col1, col2 = st.columns(2)
    col1.metric(f"Current {symbol} Price", f"${last_price}")
    col2.metric("RSI (6-Period)", round(last_rsi, 2))

    # बाय/सेल सिग्नल लॉजिक
    if last_rsi <= 30:
        st.success(f"🟢 BUY SIGNAL: RSI is Oversold ({round(last_rsi, 2)})")
    elif last_rsi >= 70:
        st.error(f"🔴 SELL SIGNAL: RSI is Overbought ({round(last_rsi, 2)})")
    else:
        st.info("⚪ Market is Neutral")

    # लाइव चार्ट (Plotly)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['time'], y=data['RSI'], name="RSI 6", line=dict(color='#FFA500')))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sell Zone")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Buy Zone")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Connecting to Exchange... {e}")
