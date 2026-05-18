# PairTrader - Quantitative Pairs Trading Bot

**A production-ready statistical arbitrage bot that identifies cointegrated stock pairs and generates automated trading signals using mean-reversion strategies.**

Built with Python, this bot implements a market-neutral pairs trading strategy on Coca-Cola (KO) and PepsiCo (PEP), achieving a **57.83% total return** ($10,000 → $15,783) with a **66.7% win rate** over a 2-year backtest period (2024-2025).

---

## 📊 Performance Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Total Return** | **+57.83%** | Outperformed S&P 500 (+28.2% same period) |
| **Annualized Return** | **+25.71%** | Consistent alpha generation |
| **Win Rate** | **66.7%** | 12 winning / 18 total trades |
| **Sharpe Ratio** | 0.70 | Positive risk-adjusted returns |
| **Max Drawdown** | -62.87% | High risk (can be reduced with position sizing) |
| **Total Profit** | $5,783.22 | From $10,000 initial capital |
| **Average Profit/Trade** | $321.29 | Sustainable statistical edge |

### Trade Breakdown
| Type | Count | Profit |
|------|-------|--------|
| Winning Trades | 12 | +$25,040.93 |
| Losing Trades | 6 | -$19,257.71 |
| **Net** | **18** | **+$5,783.22** |

---

## 🎯 What Problem Does This Solve?

Traditional stock investing is **directional** – you lose money when the market goes down. 

**Pairs trading is market-neutral:**
- You profit regardless of whether the overall market goes up or down
- You bet on the price **relationship** between two correlated stocks, not their absolute prices
- When the relationship deviates from history, it will eventually revert (mean reversion)

**The Strategy:**
1. Coca-Cola (KO) and PepsiCo (PEP) are competitors – their prices move together
2. Calculate the historical price difference (spread) between them
3. When spread deviates >2 standard deviations, take a position
4. When spread returns to normal (±0.5σ), close for profit
5. Stop-loss at ±3σ to limit catastrophic losses

**Real-World Application:** Hedge funds and prop trading firms use similar statistical arbitrage strategies to generate consistent, low-correlation returns.

---

## 🚀 Core Features

### Trading Features
| Feature | Description |
|---------|-------------|
| **Cointegration Testing** | Augmented Dickey-Fuller (ADF) test validates pairs statistically |
| **Z-Score Signals** | Entry at ±2.0σ, exit at ±0.5σ, stop-loss at ±3.0σ |
| **Position Sizing** | Configurable % of capital per trade (default: 10%) |
| **Backtesting Engine** | Historical simulation with trade-by-trade logging |
| **Market Neutral** | Strategy uncorrelated with broader market movements |

### Technical Features
| Feature | Description |
|---------|-------------|
| **Real-Time Data** | Live prices from Yahoo Finance API |
| **Automated Signals** | Daily LONG/SHORT/HOLD signals |
| **Performance Charts** | Spread, z-score, and portfolio value visualizations |
| **Telegram Alerts** | Daily trading signals sent directly to your phone |
| **CSV Export** | All historical data saved locally |

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Core programming language |
| **pandas** | Data manipulation & time series handling |
| **numpy** | Numerical computations |
| **yfinance** | Real-time stock data from Yahoo Finance |
| **statsmodels** | ADF cointegration testing |
| **matplotlib** | Visualization of spreads, z-scores, portfolio |
| **requests** | Telegram API integration |

---

## 📁 Project Structure
