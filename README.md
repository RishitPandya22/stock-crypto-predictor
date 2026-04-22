<div align="center">

# ⚡ QUANTAI TERMINAL

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&size=22&duration=3000&pause=1000&color=00D4AA&center=true&vCenter=true&width=600&lines=Real-Time+Stock+%26+Crypto+Intelligence;LSTM+Neural+Network+Predictions;Fear+%26+Greed+Index+Analysis;Live+NSE+%26+NYSE+%26+Crypto+Data" alt="Typing SVG" />

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://deepstock-ai.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.13-00d4aa?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-f7931e?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3d4db7?style=for-the-badge&logo=plotly&logoColor=white)
![Yahoo Finance](https://img.shields.io/badge/Yahoo%20Finance-Live%20Data-6001d2?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-LIVE-00ff64?style=for-the-badge)

> **A Bloomberg Terminal-inspired ML web app that predicts stock & crypto prices,
> generates BUY/SELL/HOLD signals, and analyses market sentiment — all in real time.**

🚀 **[LAUNCH LIVE APP →](https://deepstock-ai.streamlit.app)**

---

</div>

## 🎯 What Is This?

Most finance projects just plot a line chart and call it a day.

**QuantAI Terminal is different.**

It combines **machine learning price forecasting**, **technical indicator analysis**,
**market psychology scoring**, and **news sentiment** into a single Bloomberg-style
terminal interface — built entirely in Python by a first-year MDS student. 🧠

---

## ⚡ Live Features

### 🔮 ML-Powered 7-Day Price Forecast
A **Gradient Boosting Regressor** trained on engineered features including lag prices,
rolling statistics, momentum indicators and volume signals — predicts the next
7 business days of price movement with a confidence band visualisation.

### 🟢 BUY / SELL / HOLD Signal Engine
Combines **4 real technical indicators** used by professional traders:
- **RSI** (Relative Strength Index) — momentum & overbought/oversold detection
- **MACD** — trend direction and momentum crossovers
- **Bollinger Bands** — volatility and price channel analysis
- **Moving Averages (MA20/MA50/MA200)** — short, medium & long-term trend

Each indicator contributes to a weighted confidence score that produces a
final actionable signal with percentage confidence.

### 😨 Fear & Greed Index
A custom-built **market psychology meter** (0-100) calculated from:
RSI momentum, price trend vs MA50, volatility index, MACD signal
and volume momentum — displayed as an interactive gauge chart.

### 📰 News Sentiment Analysis
AI-powered sentiment scoring for each asset with positive/negative/neutral
classification, sentiment bars, and an overall bullish/bearish verdict
displayed as a donut chart.

### 🏆 Live Market Leaderboard
Real-time ranking of **10 global assets** across US stocks, crypto and
Indian NSE stocks — sorted by daily performance with live price data.

### 🇮🇳 Indian Stock Market Support
Full support for **NSE-listed Indian stocks** including Reliance, TCS,
Infosys, HDFC Bank, Zomato and more — with automatic ₹/$ currency detection.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🧠 ML Model | scikit-learn GradientBoostingRegressor | Price prediction |
| 📊 Technical Analysis | Custom Python engine | BUY/SELL/HOLD signals |
| 📈 Interactive Charts | Plotly | Candlestick, RSI, MACD charts |
| 🌐 Web App | Streamlit | Frontend & deployment |
| 📡 Live Data | yfinance (Yahoo Finance) | Real-time market data |
| 🎨 UI/UX | Custom CSS + Google Fonts | Bloomberg terminal design |
| 🚀 Deployment | Streamlit Cloud | Public live app |

---

## 🧠 ML Pipeline
Raw Price Data (Yahoo Finance)
↓
Feature Engineering
├── Lag features (1,2,3,5,10,20 days)
├── Rolling mean (5d, 20d)
├── Rolling std (5d, 20d)
├── Price momentum (5d, 20d)
├── Volume momentum
└── High-Low range ratio
↓
MinMaxScaler normalisation
↓
GradientBoostingRegressor
├── 200 estimators
├── Learning rate: 0.05
└── Max depth: 4
↓
7-Day Recursive Forecasting
└── Each prediction feeds into the next
↓
Confidence Band Visualisation

---

## 📊 Signal Engine Logic
Score = 0 (neutral baseline)
RSI < 30   → +2 (oversold = BUY)
RSI > 70   → -2 (overbought = SELL)
MA20>MA50  → +1 (bullish trend)
MA20<MA50  → -1 (bearish trend)
Price>MA200→ +1 (long-term uptrend)
MACD cross → ±1 (momentum direction)
BB touch   → ±2 (band extremes)
Score ≥ +2 → 🟢 BUY
Score ≤ -2 → 🔴 SELL
Otherwise  → 🟡 HOLD
---

## 🌍 Supported Assets

**📈 US Stocks** — Apple (AAPL), Tesla (TSLA), Google (GOOGL),
Microsoft (MSFT), Amazon (AMZN), NVIDIA (NVDA)

**₿ Crypto** — Bitcoin (BTC), Ethereum (ETH), Solana (SOL),
Dogecoin (DOGE), BNB

**🇮🇳 Indian NSE** — Reliance, TCS, Infosys, HDFC Bank, Wipro,
Adani Ports, Bajaj Finance, SBI, Tata Motors, Zomato

**📅 Historical Periods** — 6 months · 1 year · 2 years · 3 years · 5 years · 10 years

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/RishitPandya22/stock-crypto-predictor.git
cd stock-crypto-predictor

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Launch the terminal
streamlit run app.py
```

App opens at `http://localhost:8501` 🚀

---

## 📁 Project Structure
stock-crypto-predictor/
│
├── app.py              ← Streamlit web app (Bloomberg UI)
├── predictor.py        ← ML model + feature engineering
├── signals.py          ← Technical indicator engine
├── requirements.txt    ← Dependencies
│
├── data/               ← Cached price CSVs
├── models/             ← Saved model files
└── notebooks/          ← EDA & experimentation
---

## 💡 Key Data Science Concepts Demonstrated

- **Time Series Feature Engineering** — lag features, rolling statistics, momentum
- **Supervised ML for Regression** — Gradient Boosting with MinMax scaling
- **Technical Analysis** — RSI, MACD, Bollinger Bands, Moving Averages
- **Recursive Multi-Step Forecasting** — each predicted value feeds into the next
- **Sentiment Analysis** — NLP-style scoring and classification
- **Data Visualisation** — Interactive Plotly candlestick and indicator charts
- **API Integration** — Live financial data via Yahoo Finance
- **Cloud Deployment** — Production app on Streamlit Cloud

---

## ⚠️ Disclaimer

> This project is built for **educational and portfolio purposes only**.
> Nothing in this app constitutes financial advice.
> Always consult a qualified financial advisor before making investment decisions.

---

<div align="center">

## 👨‍💻 Built By

**Rishit Pandya**
Master of Data Science · University of Adelaide 🇦🇺

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077b5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/rishitpandya)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/RishitPandya22)
[![Live App](https://img.shields.io/badge/Live%20App-Launch-00d4aa?style=for-the-badge)](https://deepstock-ai.streamlit.app)

---

### 🗺️ Full Portfolio

| Project | Stack | Link |
|---|---|---|
| 🛒 Retail Sales Analysis | pandas · matplotlib · seaborn | [GitHub](https://github.com/RishitPandya22/retail-sales-analysis) |
| 🏠 Adelaide Housing Map | folium · GitHub Pages | [Live](https://rishitpandya22.github.io) |
| 🏥 AI Medical Predictor | LLaMA 3B · Django · React | [GitHub](https://github.com/RishitPandya22) |
| 🏏 Cricket Performance ML | scikit-learn · Streamlit | [Live](https://pandya-ml-app.streamlit.app) |
| ⚡ QuantAI Terminal | ML · Plotly · Streamlit | **[Live ✅](https://deepstock-ai.streamlit.app)** |

---

*If this project impressed you — imagine what I can build on your team.* 😄

</div>
