# scorecard.py
# Phase 5 — Scorecard Engine: combines FA + TA scores into final Buy/Hold/Sell

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed")

fa_path = os.path.join(PROCESSED_PATH, "fa_scores.csv")
ta_path = os.path.join(PROCESSED_PATH, "ta_scores.csv")

# ── Existence checks — point back to the right phase if something's missing ──
missing = []
if not os.path.exists(fa_path):
    missing.append(("fa_scores.csv", "fa_analysis.py (Phase 3)"))
if not os.path.exists(ta_path):
    missing.append(("ta_scores.csv", "ta_analysis.py (Phase 4)"))

if missing:
    print("❌ Cannot build the scorecard yet — missing file(s):")
    for fname, source in missing:
        print(f"   - {fname}  ->  run {source} first")
    raise SystemExit(1)

# ── Load ───────────────────────────────────────────────────────
fa_df = pd.read_csv(fa_path)
ta_df = pd.read_csv(ta_path)

# ── Merge check ────────────────────────────────────────────────
fa_stocks = set(fa_df["Stock"])
ta_stocks = set(ta_df["Stock"])
only_in_fa = fa_stocks - ta_stocks
only_in_ta = ta_stocks - fa_stocks

if only_in_fa or only_in_ta:
    print("⚠️  STOCK NAME MISMATCH between fa_scores.csv and ta_scores.csv:")
    if only_in_fa:
        print(f"   In fa_scores.csv but not ta_scores.csv: {only_in_fa}")
    if only_in_ta:
        print(f"   In ta_scores.csv but not fa_scores.csv: {only_in_ta}")
    print("   These stocks will be dropped from the final scorecard.\n")

# ── Combine ────────────────────────────────────────────────────
df = pd.merge(
    fa_df[["Stock", "FA_Score"]],
    ta_df[["Stock", "Close", "RSI_14", "TA_Score", "TA_Signal"]],
    on="Stock",
    how="inner"
)

df["Total_Score"] = (df["FA_Score"] + df["TA_Score"]).round(1)

# ── Final Buy/Hold/Sell signal (out of 100) ───────────────────────
def final_signal(score):
    if score >= 65:
        return "BUY"
    elif score >= 40:
        return "HOLD"
    else:
        return "SELL"

df["Signal"] = df["Total_Score"].apply(final_signal)

# ── Conviction: do FA and TA agree? ───────────────────────────────
def conviction(row):
    fa_bullish = row["FA_Score"] >= 25   # above midpoint of /50
    ta_bullish = row["TA_Score"] >= 25
    if fa_bullish and ta_bullish:
        return "Aligned Bullish"
    elif not fa_bullish and not ta_bullish:
        return "Aligned Bearish"
    elif fa_bullish and not ta_bullish:
        return "Mixed (FA-led)"
    else:
        return "Mixed (TA-led)"

df["Conviction"] = df.apply(conviction, axis=1)

# ── Reasoning — short, human-readable rationale per stock ─────────
def reasoning(row):
    fa_word = "strong" if row["FA_Score"] >= 30 else "weak" if row["FA_Score"] < 20 else "moderate"
    ta_word = "strong" if row["TA_Score"] >= 30 else "weak" if row["TA_Score"] < 20 else "moderate"
    rsi = row["RSI_14"]
    rsi_note = ""
    if pd.notna(rsi):
        if rsi > 70:
            rsi_note = ", though RSI suggests overbought"
        elif rsi < 30:
            rsi_note = ", though RSI suggests oversold"
    return f"{fa_word.capitalize()} fundamentals, {ta_word} technicals{rsi_note}."

df["Reasoning"] = df.apply(reasoning, axis=1)

# ── Sort and save ──────────────────────────────────────────────
df = df.sort_values("Total_Score", ascending=False).reset_index(drop=True)

out_path = os.path.join(PROCESSED_PATH, "final_scorecard.csv")
df.to_csv(out_path, index=False)

print("=" * 80)
print("  FINAL SCORECARD — FA + TA COMBINED (out of 100)")
print("=" * 80)
print(df[["Stock", "FA_Score", "TA_Score", "Total_Score", "Signal", "Conviction"]].to_string(index=False))
print(f"\n✅ Saved full scorecard to data/processed/final_scorecard.csv")