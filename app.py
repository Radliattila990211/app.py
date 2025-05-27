import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Oldalcím és beállítások
st.set_page_config(page_title="Forex Scalping Strategy", layout="wide")
st.title("📈 Forex Scalping Strategy - 5 perces időtávon")

# Devizapárok
forex_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X"]

# Időintervallum lekérdezése
end = datetime.now()
start = end - timedelta(days=7)

# Devizapár kiválasztása
symbol = st.selectbox("Válassz devizapárt:", forex_pairs)

# Adatok lekérése 5 perces időtávon
@st.cache_data(ttl=300)
def get_data(symbol):
    data = yf.download(symbol, start=start, end=end, interval="5m")
    data.dropna(inplace=True)
    return data

df = get_data(symbol)

# EMA (9 és 21)
df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()

# RSI (14)
delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

# MACD
exp1 = df["Close"].ewm(span=12, adjust=False).mean()
exp2 = df["Close"].ewm(span=26, adjust=False).mean()
df["MACD"] = exp1 - exp2
df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

# Szignál generálása
def generate_signal(row):
    if (
        row["EMA9"] > row["EMA21"] and
        row["RSI"] > 50 and
        row["MACD"] > row["Signal"]
    ):
        return "💹 BUY"
    elif (
        row["EMA9"] < row["EMA21"] and
        row["RSI"] < 50 and
        row["MACD"] < row["Signal"]
    ):
        return "🔻 SELL"
    else:
        return "⏸ NO SIGNAL"

df["Signal Decision"] = df.apply(generate_signal, axis=1)

# Legutóbbi jelzés
latest = df.iloc[-1]

st.subheader("📊 Legfrissebb adatok")
st.write(f"**Záróár:** {latest['Close']:.5f}")
st.write(f"**RSI:** {latest['RSI']:.2f}")
st.write(f"**MACD:** {latest['MACD']:.5f} / **Jelzővonal:** {latest['Signal']:.5f}")
st.write(f"**Jelzés:** {latest['Signal Decision']}")

# Chart
st.subheader("📈 Árfolyam és indikátorok")
st.line_chart(df[["Close", "EMA9", "EMA21"]].dropna())
# RSI és MACD külön ábrán (ha szeretnéd bővíthető Plotly-val is)
