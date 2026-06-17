# data_fetch.py
# Phase 2 — Fetches price data + fundamentals for all 15 NSE stocks

import yfinance as yf
import pandas as pd
import os
import time

# ── Stock Universe ─────────────────────────────────────────────
STOCKS = {
    "Reliance"   : "RELIANCE.NS",
    "TCS"        : "TCS.NS",
    "Infosys"    : "INFY.NS",
    "HDFC_Bank"  : "HDFCBANK.NS",
    "ICICI_Bank" : "ICICIBANK.NS",
    "HUL"        : "HINDUNILVR.NS",
    "ITC"        : "ITC.NS",
    "Sun_Pharma" : "SUNPHARMA.NS",
    "Dr_Reddys"  : "DRREDDY.NS",
    "Maruti"     : "MARUTI.NS",
    "Mahindra&Mahindra" : "M&M.NS",
    "Airtel"     : "BHARTIARTL.NS",
    "Tata_Steel" : "TATASTEEL.NS",
    "NTPC"       : "NTPC.NS",
    "Eternal"     : "Eternal.NS",
}

# ── Paths: anchored to this script's own location, then up to project root ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_PATH, exist_ok=True)


# ── Function 1: Fetch OHLCV Price Data ────────────────────────
def fetch_price_data(ticker_symbol, period="1y"):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    if df.empty:
        raise ValueError("No price data returned")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    return df


# ── Function 2: Fetch Fundamental Snapshot (always returns a row) ──
def fetch_fundamental_data(name, ticker_symbol):
    keys = [
        "currentPrice", "marketCap", "trailingPE", "priceToBook",
        "returnOnEquity", "debtToEquity", "trailingEps",
        "revenueGrowth", "earningsGrowth", "dividendYield",
        "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
    ]

    data = {"Stock": name, "Ticker": ticker_symbol}

    try:
        info = yf.Ticker(ticker_symbol).info
        for key in keys:
            data[key] = info.get(key, "N/A")
    except Exception:
        for key in keys:
            data[key] = "N/A"

    return data


# ── Main Runner ────────────────────────────────────────────────
if __name__ == "__main__":
    fundamental_list = []

    print("=" * 55)
    print("     FETCHING DATA FOR ALL 15 STOCKS")
    print("=" * 55)

    for name, ticker in STOCKS.items():
        print(f"\n📥 {name} ({ticker})")

        try:
            price_df = fetch_price_data(ticker, period="1y")
            csv_path = os.path.join(RAW_PATH, f"{name}_price.csv")
            price_df.to_csv(csv_path)
            print(f"   ✅ Price data saved | {len(price_df)} rows")
        except Exception as e:
            print(f"   ❌ Price fetch failed: {e}")

        fund_data = fetch_fundamental_data(name, ticker)
        fundamental_list.append(fund_data)
        print(f"   ✅ Fundamentals recorded")

        time.sleep(1)  # avoid Yahoo's rate limit on bulk requests

    fund_df = pd.DataFrame(fundamental_list)
    fund_path = os.path.join(RAW_PATH, "fundamentals_raw.csv")
    fund_df.to_csv(fund_path, index=False)

    print("\n" + "=" * 55)
    print("  ✅ ALL DATA SAVED SUCCESSFULLY!")
    print(f"  📁 Price CSVs   → {RAW_PATH}")
    print(f"  📊 Fundamentals → {fund_path}")
    print("=" * 55)