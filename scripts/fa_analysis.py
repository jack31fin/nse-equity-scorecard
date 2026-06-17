# fa_analysis.py
# Phase 3 — Fundamental Analysis scoring

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROCESSED_PATH, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────
fund_df = pd.read_csv(os.path.join(RAW_PATH, "fundamentals_raw.csv"))
screener_df = pd.read_csv(os.path.join(RAW_PATH, "screener_data.csv"))

# ── Clean screener_data.csv (handles "%", stray spaces, "NA") ──
def clean_pct(val):
    if pd.isna(val):
        return float("nan")
    val = str(val).strip().rstrip("%").strip()
    if val.upper() in ("NA", "N/A", ""):
        return float("nan")
    try:
        return float(val)
    except ValueError:
        return float("nan")

screener_df["Stock"] = screener_df["Stock"].str.strip()
for col in ["ROCE", "Promoter_Holding", "Rev_CAGR_3Y", "PAT_CAGR_3Y", "OPM"]:
    screener_df[col] = screener_df[col].apply(clean_pct)

# ── Merge check — surfaces name mismatches instead of failing silently ──
fund_stocks = set(fund_df["Stock"])
screener_stocks = set(screener_df["Stock"])
only_in_fund = fund_stocks - screener_stocks
only_in_screener = screener_stocks - fund_stocks

if only_in_fund or only_in_screener:
    print("⚠️  STOCK NAME MISMATCH DETECTED:")
    if only_in_fund:
        print(f"   In fundamentals_raw.csv but not screener_data.csv: {only_in_fund}")
    if only_in_screener:
        print(f"   In screener_data.csv but not fundamentals_raw.csv: {only_in_screener}")
    print("   These stocks will have incomplete rows below — fix the names and re-run.\n")

# ── Merge ──────────────────────────────────────────────────────
df = pd.merge(fund_df, screener_df, on="Stock", how="outer")

# ── Normalize yfinance numeric columns ───────────────────────────
numeric_cols = ["trailingPE", "priceToBook", "returnOnEquity",
                 "debtToEquity", "revenueGrowth", "earningsGrowth", "dividendYield"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# yfinance returns ROE/growth as decimals (0.18) — convert to % to match Screener scale
df["returnOnEquity"] = df["returnOnEquity"] * 100
df["revenueGrowth"] = df["revenueGrowth"] * 100
df["earningsGrowth"] = df["earningsGrowth"] * 100

# ── Percentile-rank scoring ───────────────────────────────────────
# Each metric is ranked 0-1 across your 15 stocks (1 = best in the group).
# "Lower is better" metrics (P/E, P/B, D/E) are inverted. Missing data gets
# a neutral 0.5 so one blank field doesn't tank a stock's score.
def rank_score(series, lower_is_better=False):
    pct = series.rank(pct=True, na_option="keep")
    if lower_is_better:
        pct = 1 - pct
    return pct.fillna(0.5)

scores = pd.DataFrame({"Stock": df["Stock"]})

# Valuation — 10 pts (cheaper P/E & P/B score higher)
scores["Valuation"] = (
    rank_score(df["trailingPE"], lower_is_better=True) * 0.5 +
    rank_score(df["priceToBook"], lower_is_better=True) * 0.5
) * 10

# Profitability — 15 pts (higher ROE, ROCE, OPM = better)
scores["Profitability"] = (
    rank_score(df["returnOnEquity"]) / 3 +
    rank_score(df["ROCE"]) / 3 +
    rank_score(df["OPM"]) / 3
) * 15

# Growth — 15 pts: blends Screener's 3Y CAGR (medium-term trend)
# with yfinance's latest YoY growth (recent momentum)
scores["Growth"] = (
    rank_score(df["Rev_CAGR_3Y"]) * 0.25 +
    rank_score(df["PAT_CAGR_3Y"]) * 0.25 +
    rank_score(df["revenueGrowth"]) * 0.25 +
    rank_score(df["earningsGrowth"]) * 0.25
) * 15

# Financial Health — 5 pts (lower D/E = better)
scores["Financial_Health"] = rank_score(df["debtToEquity"], lower_is_better=True) * 5

# Ownership — 5 pts (higher promoter holding = more skin in the game)
scores["Ownership"] = rank_score(df["Promoter_Holding"]) * 5

scores["FA_Score"] = scores[
    ["Valuation", "Profitability", "Growth", "Financial_Health", "Ownership"]
].sum(axis=1).round(1)

# ── Combine, sort, save ────────────────────────────────────────────
result = df.merge(scores, on="Stock")
result = result.sort_values("FA_Score", ascending=False).reset_index(drop=True)

out_path = os.path.join(PROCESSED_PATH, "fa_scores.csv")
result.to_csv(out_path, index=False)

print("=" * 60)
print("  FUNDAMENTAL ANALYSIS SCORES (out of 50)")
print("=" * 60)
print(result[["Stock", "Valuation", "Profitability", "Growth",
               "Financial_Health", "Ownership", "FA_Score"]].to_string(index=False))
print(f"\n✅ Saved full results to data/processed/fa_scores.csv")