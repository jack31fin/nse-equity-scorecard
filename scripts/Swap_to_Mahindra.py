# scripts/swap_to_mahindra.py
# One-time fix: replace Tata Motors with Mahindra & Mahindra (M&M)
'''
import yfinance as yf
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw")

NEW_NAME = "Mahindra_Mahindra"
NEW_TICKER = "M&M.NS"

KEYS = [
    "currentPrice", "marketCap", "trailingPE", "priceToBook",
    "returnOnEquity", "debtToEquity", "trailingEps",
    "revenueGrowth", "earningsGrowth", "dividendYield",
    "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
]

ticker = yf.Ticker(NEW_TICKER)

# 1. Price data
price_df = ticker.history(period="1y")
if price_df.empty:
    raise SystemExit(f"❌ No price data for {NEW_TICKER} — check the ticker on Yahoo Finance.")
price_df.index = pd.to_datetime(price_df.index).tz_localize(None)
price_df = price_df[["Open", "High", "Low", "Close", "Volume"]]
price_df.to_csv(os.path.join(RAW_PATH, f"{NEW_NAME}_price.csv"))
print(f"✅ Saved {NEW_NAME}_price.csv | {len(price_df)} rows")

# 2. Fundamentals
fund_row = {"Stock": NEW_NAME, "Ticker": NEW_TICKER}
try:
    info = ticker.info
    for key in KEYS:
        fund_row[key] = info.get(key, "N/A")
except Exception:
    for key in KEYS:
        fund_row[key] = "N/A"

# 3. Replace Tata_Motors row in fundamentals_raw.csv
fund_path = os.path.join(RAW_PATH, "fundamentals_raw.csv")
fund_df = pd.read_csv(fund_path)
fund_df = fund_df[fund_df["Stock"] != "Tata_Motors"]
fund_df = pd.concat([fund_df, pd.DataFrame([fund_row])], ignore_index=True)
fund_df.to_csv(fund_path, index=False)
print(f"✅ fundamentals_raw.csv updated — Tata_Motors removed, {NEW_NAME} added")

print("\nNow in screener_data.csv, update two row labels:")
print(f"  1. 'M_M'     → '{NEW_NAME}'")
print(f"  2. 'Eternal' → 'Zomato'   (matches fundamentals_raw.csv naming for now)")'''