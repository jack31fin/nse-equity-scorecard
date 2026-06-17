# ta_analysis.py
# Phase 4 — Technical Analysis indicators + scoring

import pandas as pd
import pandas_ta_classic as ta
import os
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROCESSED_PATH, exist_ok=True)

# ── Discover all price files in data/raw/ ─────────────────────────
price_files = glob.glob(os.path.join(RAW_PATH, "*_price.csv"))

ta_rows = []

for filepath in sorted(price_files):
    stock_name = os.path.basename(filepath).replace("_price.csv", "")

    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    if len(df) < 200:
        print(f"⚠️  {stock_name}: only {len(df)} rows — SMA_200 will be NaN")

    # ── Indicators via pandas_ta_classic ──────────────────────────
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)

    # Volume confirmation — plain pandas rolling average
    df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()

    # Save full indicator-augmented data — useful for Phase 6 charts
    df.to_csv(os.path.join(PROCESSED_PATH, f"{stock_name}_indicators.csv"))

    # ── Latest snapshot ────────────────────────────────────────────
    latest = df.iloc[-1]
    close = latest["Close"]
    sma50 = latest["SMA_50"]
    sma200 = latest["SMA_200"]
    ema20 = latest["EMA_20"]
    rsi = latest["RSI_14"]
    macd = latest["MACD_12_26_9"]
    macd_signal = latest["MACDs_12_26_9"]
    volume = latest["Volume"]
    vol_sma20 = latest["Volume_SMA_20"]

    # ── Scoring (out of 50) ────────────────────────────────────────
    # Trend — 15 pts: price above SMA50, and SMA50 above SMA200 (golden cross structure)
    trend_score = 0
    trend_score += 7.5 if close > sma50 else 0
    trend_score += 7.5 if (pd.notna(sma200) and sma50 > sma200) else 0

    # Momentum (RSI) — 10 pts: 50-70 = healthy bullish zone, >70 overbought, <30 oversold
    if pd.isna(rsi):
        rsi_score = 5
    elif 50 <= rsi <= 70:
        rsi_score = 10
    elif rsi > 70:
        rsi_score = 3
    elif 30 <= rsi < 50:
        rsi_score = 6
    else:
        rsi_score = 5

    # MACD — 10 pts: bullish crossover (5) + MACD above zero line (5)
    if pd.notna(macd) and pd.notna(macd_signal):
        macd_score = (5 if macd > macd_signal else 0) + (5 if macd > 0 else 0)
    else:
        macd_score = 5

    # EMA20 — 10 pts: price above short-term average = short-term bullish
    ema_score = 10 if (pd.notna(ema20) and close > ema20) else 0

    # Volume — 5 pts: latest volume above its 20-day average confirms the move
    if pd.isna(vol_sma20):
        vol_score = 2.5
    else:
        vol_score = 5 if volume > vol_sma20 else 0

    ta_score = round(trend_score + rsi_score + macd_score + ema_score + vol_score, 1)

    # ── Auto Buy/Sell flag ─────────────────────────────────────────
    if ta_score >= 35:
        signal = "BUY"
    elif ta_score >= 20:
        signal = "HOLD"
    else:
        signal = "SELL"

    ta_rows.append({
        "Stock": stock_name,
        "Close": round(close, 2),
        "SMA_50": round(sma50, 2) if pd.notna(sma50) else None,
        "SMA_200": round(sma200, 2) if pd.notna(sma200) else None,
        "EMA_20": round(ema20, 2) if pd.notna(ema20) else None,
        "RSI_14": round(rsi, 2) if pd.notna(rsi) else None,
        "MACD": round(macd, 2) if pd.notna(macd) else None,
        "MACD_Signal": round(macd_signal, 2) if pd.notna(macd_signal) else None,
        "Trend_Score": trend_score,
        "RSI_Score": rsi_score,
        "MACD_Score": macd_score,
        "EMA_Score": ema_score,
        "Volume_Score": vol_score,
        "TA_Score": ta_score,
        "TA_Signal": signal,
    })

# ── Save summary ──────────────────────────────────────────────────
ta_df = pd.DataFrame(ta_rows).sort_values("TA_Score", ascending=False).reset_index(drop=True)

out_path = os.path.join(PROCESSED_PATH, "ta_scores.csv")
ta_df.to_csv(out_path, index=False)

print("=" * 70)
print("  TECHNICAL ANALYSIS SCORES (out of 50)")
print("=" * 70)
print(ta_df[["Stock", "Close", "RSI_14", "TA_Score", "TA_Signal"]].to_string(index=False))
print(f"\n✅ Saved full results to data/processed/ta_scores.csv")
print(f"✅ Saved per-stock indicator data to data/processed/<Stock>_indicators.csv")