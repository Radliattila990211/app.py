import streamlit as st
import pandas as pd
import requests
import ta

st.set_page_config(page_title="Forex Scalping 5min", layout="wide")

st.title("💹 Forex Scalping Jelzések (5 perces stratégia)")
st.write("Indikátorok: EMA (9/21), RSI (14), MACD — Adatok: Alpha Vantage")

API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]

symbol_map = {
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD",
    "NZD/USD": "NZDUSD",
    "USD/CAD": "USDCAD",
    "EUR/JPY": "EURJPY",
    "GBP/JPY": "GBPJPY",
    "EUR/GBP": "EURGBP"
}

pair = st.selectbox("Válassz devizapárt", list(symbol_map.keys()))
symbol = symbol_map[pair]

@st.cache_data(ttl=300)
def load_data(symbol):
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={symbol[:3]}&to_symbol={symbol[3:]}&interval=5min&apikey={API_KEY}&outputsize=compact"
    r = requests.get(url)
    data = r.json()
    if "Time Series FX (5min)" not in data:
        st.error("Hiba az API válaszban. Lehet, hogy túl sok kérés történt. Próbáld újra később.")
        return None
    df = pd.DataFrame(data["Time Series FX (5min)"]).T.astype(float)
    df.columns = ["open", "high", "low", "close"]
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

df = load_data(symbol)

if df is not None:
    # Indikátorok számítása
    df["EMA9"] = ta.trend.ema_indicator(df["close"], window=9)
    df["EMA21"] = ta.trend.ema_indicator(df["close"], window=21)
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    macd = ta.trend.macd(df["close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    last = df.iloc[-1]
    signal = ""

    # Stratégiák kombinálása
    if last["EMA9"] > last["EMA21"] and last["RSI"] > 50 and last["MACD"] > last["MACD_signal"]:
        signal = "📈 **Vételi jelzés**"
    elif last["EMA9"] < last["EMA21"] and last["RSI"] < 50 and last["MACD"] < last["MACD_signal"]:
        signal = "📉 **Eladási jelzés**"
    else:
        signal = "⏳ Nincs egyértelmű jelzés"

    st.metric("Aktuális záróár", f"{last['close']:.5f}")
    st.subheader("Jelzés:")
    st.markdown(signal)

    with st.expander("📊 Részletes adatok és indikátorok"):
        st.dataframe(df.tail(20).iloc[::-1])
