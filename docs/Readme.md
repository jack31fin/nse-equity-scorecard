# NSE Equity Scorecard — Combined FA + TA Buy/Sell Signal Tracker

A Python-based equity screening tool that scores 15 NSE-listed stocks across 9 sectors using a combined Fundamental Analysis (FA) and Technical Analysis (TA) framework, producing a weighted Buy/Hold/Sell signal for each stock.

## Overview

Built to apply fundamental and technical analysis concepts through a reproducible, code-driven scoring system rather than subjective, one-off stock calls. Each stock is scored out of 100 — 50 points from fundamentals, 50 from technicals — and the combined score determines the final signal.

## Stock Universe

15 stocks across Energy, IT, Banking, FMCG, Pharma, Auto, Telecom, Metals, and Power — large-caps and PSUs mixed with one new-age tech name (Zomato/Eternal) for breadth.

## Methodology

**Fundamental Analysis (50 pts):** Valuation (P/E, P/B), Profitability (ROE, ROCE, OPM), Growth (3Y revenue/profit CAGR + latest YoY growth), Financial Health (Debt/Equity), Ownership (Promoter Holding). Each metric is percentile-ranked across the 15-stock universe rather than scored against fixed thresholds, since "good" P/E for an IT company looks nothing like a bank's.

**Technical Analysis (50 pts):** Trend (price vs SMA50/SMA200), Momentum (RSI-14), MACD crossover, short-term trend (EMA20), Volume confirmation.

**Final Signal:** Total Score ≥70 = BUY · 45–69 = HOLD · below 45 = SELL.

## Tech Stack

Python (pandas, yfinance, pandas-ta-classic, openpyxl). Manual sourcing from Screener.in for metrics yfinance doesn't expose for Indian equities — ROCE, Promoter Holding, multi-year CAGRs.

## Project Structure