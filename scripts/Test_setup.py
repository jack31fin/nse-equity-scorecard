import yfinance as yf
import pandas as pd
import pandas_ta_classic as ta
import matplotlib.pyplot as plt

ticker = yf.Ticker("TCS.NS")
df = ticker.history(period="6mo")
print(df.tail())

df.ta.rsi(length=14, append=True)
print(df[["Close", "RSI_14"]].tail())

print("✅ Setup successful — all libraries working!")