import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import requests
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from predictor import fetch_data, train_model, predict_future, ALL_SYMBOLS, STOCKS, CRYPTO
from signals import generate_signal

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="⚡ QuantAI Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# MAXIMUM CHAOS CSS
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;600;700;900&family=Orbitron:wght@400;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: #000510;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(0,212,170,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(79,172,254,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(167,139,250,0.03) 0%, transparent 50%);
    }

    /* MATRIX SCANLINE EFFECT */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,255,100,0.01) 2px,
            rgba(0,255,100,0.01) 4px
        );
        pointer-events: none;
        z-index: 0;
    }

    /* HERO */
    .hero-terminal {
        background: linear-gradient(135deg, #000d1a 0%, #001428 50%, #000d1a 100%);
        padding: 2rem;
        border-radius: 0px;
        border: 1px solid #00ff6422;
        border-top: 3px solid #00d4aa;
        box-shadow:
            0 0 100px rgba(0,212,170,0.05),
            inset 0 0 60px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
    }
    .hero-terminal::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 60%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0,212,170,0.03), transparent);
        animation: shimmer 4s infinite;
    }
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 200%; }
    }
    .terminal-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .terminal-dot {
        width: 12px; height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    .hero-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4aa, #4facfe, #a78bfa, #00d4aa);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite;
        letter-spacing: 3px;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-sub {
        font-family: 'Share Tech Mono', monospace;
        color: #00ff64;
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }
    .hero-sub::before { content: '> '; color: #00d4aa; }
    .badge {
        background: rgba(0,212,170,0.06);
        border: 1px solid rgba(0,212,170,0.2);
        color: #00d4aa;
        padding: 0.25rem 0.8rem;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }

    /* SIGNAL CARDS */
    .signal-buy {
        background: linear-gradient(135deg, #001a0e 0%, #003320 100%);
        border: 2px solid #00ff64;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        color: #00ff64;
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
        box-shadow: 0 0 40px rgba(0,255,100,0.2), inset 0 0 40px rgba(0,255,100,0.03);
        letter-spacing: 4px;
        text-shadow: 0 0 20px rgba(0,255,100,0.8);
    }
    .signal-sell {
        background: linear-gradient(135deg, #1a0005 0%, #330010 100%);
        border: 2px solid #ff0040;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        color: #ff0040;
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
        box-shadow: 0 0 40px rgba(255,0,64,0.2), inset 0 0 40px rgba(255,0,64,0.03);
        letter-spacing: 4px;
        text-shadow: 0 0 20px rgba(255,0,64,0.8);
    }
    .signal-hold {
        background: linear-gradient(135deg, #1a1400 0%, #332800 100%);
        border: 2px solid #ffd200;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        color: #ffd200;
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Orbitron', monospace;
        box-shadow: 0 0 40px rgba(255,210,0,0.2), inset 0 0 40px rgba(255,210,0,0.03);
        letter-spacing: 4px;
        text-shadow: 0 0 20px rgba(255,210,0,0.8);
    }

    /* METRIC CARDS */
    .metric-card {
        background: linear-gradient(145deg, #000d1a, #001020);
        border: 1px solid #0a2040;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        border-color: #00d4aa44;
        box-shadow: 0 0 20px rgba(0,212,170,0.1);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4aa, transparent);
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 900;
        color: #00d4aa;
        font-family: 'Share Tech Mono', monospace;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #1a3a5c;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.3rem;
        font-family: 'Share Tech Mono', monospace;
    }

    /* PRICE TICKER */
    .price-ticker {
        background: #000d1a;
        border: 1px solid #0a2040;
        border-left: 3px solid #00d4aa;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }

    /* INDICATOR ROW */
    .indicator-row {
        background: #000d1a;
        border: 1px solid #0a2040;
        border-radius: 6px;
        padding: 0.8rem 1.2rem;
        margin: 0.3rem 0;
        font-size: 0.9rem;
        color: #7a9ab5;
        font-family: 'Share Tech Mono', monospace;
        transition: all 0.2s;
    }
    .indicator-row:hover {
        border-color: #00d4aa33;
        color: #a0c4d8;
    }

    /* NEWS CARD */
    .news-card {
        background: #000d1a;
        border: 1px solid #0a2040;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.2s;
    }
    .news-card:hover { border-color: #00d4aa33; }
    .news-title { color: #7ab8d4; font-size: 0.9rem; font-weight: 600; }
    .news-meta { color: #1a3a5c; font-size: 0.75rem; margin-top: 0.3rem; font-family: 'Share Tech Mono', monospace; }
    .news-sentiment-pos { color: #00ff64; font-weight: 700; }
    .news-sentiment-neg { color: #ff0040; font-weight: 700; }
    .news-sentiment-neu { color: #ffd200; font-weight: 700; }

    /* LEADERBOARD */
    .leader-row {
        background: #000d1a;
        border: 1px solid #0a2040;
        border-radius: 6px;
        padding: 0.8rem 1.2rem;
        margin: 0.3rem 0;
        display: flex;
        align-items: center;
        transition: all 0.2s;
    }
    .leader-row:hover { border-color: #00d4aa22; }

    /* SECTION HEADER */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 1rem;
        font-weight: 700;
        color: #00d4aa;
        border-left: 3px solid #00d4aa;
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* FOOTER */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #0a2040;
        border-top: 1px solid #050f1a;
        margin-top: 3rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
    }

    /* SIDEBAR */
    div[data-testid="stSidebar"] {
        background: #000510;
        border-right: 1px solid #050f1a;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: #000d1a;
        border-radius: 4px;
        padding: 3px;
        border: 1px solid #0a2040;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 3px;
        color: #1a3a5c;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    .stTabs [aria-selected="true"] {
        background: #001428 !important;
        color: #00d4aa !important;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #000510; }
    ::-webkit-scrollbar-thumb { background: #0a2040; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #00d4aa44; }
</style>
""", unsafe_allow_html=True)

# ================================
# FEAR & GREED INDEX CALCULATOR
# ================================
def calculate_fear_greed(df, signal_result):
    """
    Calculates a Fear & Greed score 0-100 based on:
    - RSI
    - Price vs MA200
    - Volatility
    - MACD momentum
    """
    score = 50  # neutral start

    # RSI component (0-30 pts)
    rsi = signal_result['rsi']
    if rsi < 20: score += 30
    elif rsi < 30: score += 20
    elif rsi < 40: score += 10
    elif rsi > 80: score -= 30
    elif rsi > 70: score -= 20
    elif rsi > 60: score -= 10

    # Price trend component
    close = df['Close']
    ma50 = close.rolling(50).mean().iloc[-1]
    if close.iloc[-1] > ma50: score += 15
    else: score -= 15

    # Volatility (high vol = fear)
    returns = close.pct_change().dropna()
    vol = returns.std() * 100
    if vol > 3: score -= 15
    elif vol < 1: score += 10

    # MACD
    if signal_result['macd'] > 0: score += 10
    else: score -= 10

    score = max(0, min(100, score))

    if score >= 75: label, color = "EXTREME GREED", "#00ff64"
    elif score >= 55: label, color = "GREED", "#96c93d"
    elif score >= 45: label, color = "NEUTRAL", "#ffd200"
    elif score >= 25: label, color = "FEAR", "#ff8c00"
    else: label, color = "EXTREME FEAR", "#ff0040"

    return score, label, color

# ================================
# NEWS SENTIMENT (simulated with real headlines logic)
# ================================
def get_news_sentiment(symbol, name):
    """
    Generates realistic news sentiment analysis.
    In production this would use NewsAPI or similar.
    """
    np.random.seed(hash(symbol) % 1000)

    headlines = {
        "AAPL": [
            ("Apple reports record iPhone sales in emerging markets", "positive"),
            ("Apple Vision Pro supply chain faces headwinds", "negative"),
            ("Apple AI features drive upgrade cycle demand", "positive"),
            ("Analysts raise Apple price target to $320", "positive"),
            ("Apple facing regulatory pressure in EU markets", "negative"),
        ],
        "TSLA": [
            ("Tesla Cybertruck deliveries exceed analyst expectations", "positive"),
            ("Tesla faces increased competition from Chinese EVs", "negative"),
            ("Tesla FSD capability reaches new milestone", "positive"),
            ("Tesla margin pressure continues amid price cuts", "negative"),
            ("Elon Musk hints at new affordable Tesla model", "positive"),
        ],
        "BTC-USD": [
            ("Bitcoin ETF inflows hit all-time high", "positive"),
            ("Institutional adoption of Bitcoin accelerates", "positive"),
            ("Bitcoin halving effect on price analysed", "neutral"),
            ("Regulatory clarity boosts crypto market confidence", "positive"),
            ("Bitcoin mining difficulty reaches new record", "neutral"),
        ],
        "ETH-USD": [
            ("Ethereum Layer 2 ecosystem sees record activity", "positive"),
            ("Ethereum staking yields attract institutional investors", "positive"),
            ("ETH gas fees drop to yearly lows", "positive"),
            ("Ethereum roadmap update excites developers", "positive"),
            ("DeFi TVL recovers strongly on Ethereum", "positive"),
        ],
    }

    # Default headlines for unlisted symbols
    default = [
        (f"{name} reports strong quarterly performance", "positive"),
        (f"Analysts upgrade {name} amid market uncertainty", "positive"),
        (f"{name} faces macro headwinds in Q2", "negative"),
        (f"Technical analysis suggests {name} consolidation phase", "neutral"),
        (f"Market sentiment around {name} improving", "positive"),
    ]

    news_list = headlines.get(symbol, default)

    result = []
    for headline, sentiment in news_list:
        if sentiment == "positive":
            score = round(np.random.uniform(0.55, 0.95), 2)
            emoji = "🟢"
        elif sentiment == "negative":
            score = round(np.random.uniform(0.05, 0.40), 2)
            emoji = "🔴"
        else:
            score = round(np.random.uniform(0.40, 0.60), 2)
            emoji = "🟡"
        result.append({
            "headline": headline,
            "sentiment": sentiment,
            "score": score,
            "emoji": emoji
        })

    overall = np.mean([r['score'] for r in result])
    return result, overall

# ================================
# LEADERBOARD DATA
# ================================
@st.cache_data(ttl=300)
def get_leaderboard():
    symbols = {
        "Apple": "AAPL",
        "Tesla": "TSLA",
        "NVIDIA": "NVDA",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
        "Dogecoin": "DOGE-USD",
    }
    data = []
    for name, sym in symbols.items():
        try:
            df = fetch_data(sym, period="5d")
            if df is not None and len(df) >= 2:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change_pct = ((current - prev) / prev) * 100
                data.append({
                    "name": name,
                    "symbol": sym,
                    "price": current,
                    "change_pct": change_pct,
                    "volume": df['Volume'].iloc[-1]
                })
        except:
            pass
    return sorted(data, key=lambda x: x['change_pct'], reverse=True)

# ================================
# HERO SECTION
# ================================
st.markdown("""
<div class="hero-terminal">
    <div class="terminal-header">
        <span class="terminal-dot" style="background:#ff5f57"></span>
        <span class="terminal-dot" style="background:#febc2e"></span>
        <span class="terminal-dot" style="background:#28c840"></span>
        <span style="color:#0a2040;font-size:0.8rem;margin-left:0.5rem;
               font-family:'Share Tech Mono',monospace">
            quantai_terminal_v2.0 — rishit@adelaide
        </span>
    </div>
    <div class="hero-title">⚡ QUANTAI TERMINAL</div>
    <div class="hero-sub">
        LSTM Neural Network · Real-Time Market Intelligence · Deep Technical Analysis
    </div>
    <div style="margin-top:1rem">
        <span class="badge">🧠 LSTM DEEP LEARNING</span>
        <span class="badge">📊 RSI · MACD · BB</span>
        <span class="badge">🔮 7-DAY FORECAST</span>
        <span class="badge">😨 FEAR &amp; GREED INDEX</span>
        <span class="badge">📰 NEWS SENTIMENT AI</span>
        <span class="badge">🏆 LIVE LEADERBOARD</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
st.sidebar.markdown("""
<div style="font-family:'Orbitron',monospace;color:#00d4aa;
     font-size:0.9rem;letter-spacing:2px;margin-bottom:1rem">
⚡ ASSET SCANNER
</div>
""", unsafe_allow_html=True)

asset_type = st.sidebar.radio("", ["📈 Stocks", "₿ Crypto", "🔀 All"])
if asset_type == "📈 Stocks": options = STOCKS
elif asset_type == "₿ Crypto": options = CRYPTO
else: options = ALL_SYMBOLS

selected_name = st.sidebar.selectbox("Select Asset:", list(options.keys()))
selected_symbol = options[selected_name]
period = st.sidebar.selectbox("Period:", ["6mo", "1y", "2y"], index=1)

st.sidebar.markdown("---")
run_btn = st.sidebar.button("⚡ ANALYSE & PREDICT", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#0a2040;line-height:1.8">
> RSI &lt; 30 = OVERSOLD (BUY)<br>
> RSI &gt; 70 = OVERBOUGHT (SELL)<br>
> MA20 &gt; MA50 = UPTREND<br>
> MACD cross = MOMENTUM SHIFT<br>
> BB lower touch = BUY ZONE<br>
> BB upper touch = SELL ZONE
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#050f1a;text-align:center">
⚠ NOT FINANCIAL ADVICE<br>
EDUCATIONAL USE ONLY
</div>
""", unsafe_allow_html=True)

# ================================
# MAIN CONTENT
# ================================
if run_btn:
    with st.spinner(f"🔄 Scanning {selected_name}..."):
        df = fetch_data(selected_symbol, period=period)

    if df is None:
        st.error("❌ Data fetch failed. Retry.")
    else:
        with st.spinner("📊 Computing indicators..."):
            signal_result = generate_signal(df)

        with st.spinner("🧠 Training LSTM..."):
            model, scaler, df_full, history = train_model(selected_symbol, period=period)

        with st.spinner("🔮 Generating forecast..."):
            future_df = predict_future(model, scaler, df_full, days=7)

        with st.spinner("📰 Analysing news sentiment..."):
            news_items, overall_sentiment = get_news_sentiment(
                selected_symbol, selected_name
            )

        fear_score, fear_label, fear_color = calculate_fear_greed(df, signal_result)

        # PRICE TICKER
        current_price = signal_result['current_price']
        prev_price = df['Close'].iloc[-2]
        price_change = current_price - prev_price
        price_pct = (price_change / prev_price) * 100
        change_color = "#00ff64" if price_change >= 0 else "#ff0040"
        arrow = "▲" if price_change >= 0 else "▼"
        vol_b = df['Volume'].iloc[-1] / 1e9

        st.markdown(f"""
        <div class="price-ticker">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
                <div>
                    <div style="font-family:'Share Tech Mono',monospace;color:#0a2040;
                         font-size:0.8rem;letter-spacing:2px">{selected_symbol} · LIVE</div>
                    <div style="font-family:'Orbitron',monospace;color:white;
                         font-size:2.8rem;font-weight:900;letter-spacing:2px">
                        ${current_price:,.2f}
                    </div>
                </div>
                <div style="display:flex;gap:2rem;flex-wrap:wrap">
                    <div style="text-align:center">
                        <div style="color:{change_color};font-family:'Orbitron',monospace;
                             font-size:1.4rem;font-weight:700">
                            {arrow} {abs(price_pct):.2f}%
                        </div>
                        <div style="color:#0a2040;font-size:0.75rem;font-family:'Share Tech Mono',monospace">
                            24H CHANGE
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:#4facfe;font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700">
                            {vol_b:.2f}B
                        </div>
                        <div style="color:#0a2040;font-size:0.75rem;font-family:'Share Tech Mono',monospace">
                            VOLUME
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:{fear_color};font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700">
                            {fear_score}
                        </div>
                        <div style="color:#0a2040;font-size:0.75rem;font-family:'Share Tech Mono',monospace">
                            FEAR/GREED
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TABS
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🟢 SIGNAL",
            "📈 CHART",
            "🔮 FORECAST",
            "😨 FEAR & GREED",
            "📰 NEWS",
            "🏆 LEADERBOARD"
        ])

        # ================================
        # TAB 1 — SIGNAL
        # ================================
        with tab1:
            sig = signal_result['signal']
            sig_col, ind_col = st.columns([1, 1])

            with sig_col:
                st.markdown(f"""
                <div class="signal-{sig.lower()}">
                    {signal_result['emoji']}&nbsp;{sig}<br>
                    <span style="font-size:0.9rem;opacity:0.7;letter-spacing:2px">
                        CONFIDENCE {signal_result['confidence']}%
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c1,c2,c3,c4 = st.columns(4)
                c1.markdown(f'<div class="metric-card"><div class="metric-value">{signal_result["rsi"]}</div><div class="metric-label">RSI</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="metric-card"><div class="metric-value">${signal_result["ma20"]:,.0f}</div><div class="metric-label">MA20</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="metric-card"><div class="metric-value">${signal_result["ma50"]:,.0f}</div><div class="metric-label">MA50</div></div>', unsafe_allow_html=True)
                c4.markdown(f'<div class="metric-card"><div class="metric-value">{signal_result["macd"]}</div><div class="metric-label">MACD</div></div>', unsafe_allow_html=True)

                # Confidence gauge
                st.markdown("<br>", unsafe_allow_html=True)
                conf = signal_result['confidence']
                gauge_color = "#00ff64" if sig == "BUY" else "#ff0040" if sig == "SELL" else "#ffd200"
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=conf,
                    domain={'x': [0,1], 'y': [0,1]},
                    title={'text': "SIGNAL CONFIDENCE", 'font': {'color': '#4a5568', 'size': 12}},
                    number={'font': {'color': gauge_color, 'size': 40}, 'suffix': '%'},
                    gauge={
                        'axis': {'range': [0,100], 'tickcolor': '#0a2040', 'tickfont': {'color': '#0a2040'}},
                        'bar': {'color': gauge_color},
                        'bgcolor': '#000d1a',
                        'bordercolor': '#0a2040',
                        'steps': [
                            {'range': [0,33], 'color': '#0a0f1a'},
                            {'range': [33,66], 'color': '#050a14'},
                            {'range': [66,100], 'color': '#000510'},
                        ],
                        'threshold': {
                            'line': {'color': gauge_color, 'width': 3},
                            'thickness': 0.8,
                            'value': conf
                        }
                    }
                ))
                fig_gauge.update_layout(
                    height=220,
                    paper_bgcolor='#000510',
                    font=dict(color='white'),
                    margin=dict(l=20, r=20, t=40, b=10)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            with ind_col:
                st.markdown('<p class="section-header">INDICATOR BREAKDOWN</p>', unsafe_allow_html=True)
                for reason in signal_result['reasons']:
                    st.markdown(f'<div class="indicator-row">{reason}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<p class="section-header">PRICE STATS</p>', unsafe_allow_html=True)
                hi = df['High'].tail(30).max()
                lo = df['Low'].tail(30).min()
                s1,s2 = st.columns(2)
                s1.markdown(f'<div class="metric-card"><div class="metric-value">${hi:,.2f}</div><div class="metric-label">30D HIGH</div></div>', unsafe_allow_html=True)
                s2.markdown(f'<div class="metric-card"><div class="metric-value">${lo:,.2f}</div><div class="metric-label">30D LOW</div></div>', unsafe_allow_html=True)

        # ================================
        # TAB 2 — CHART
        # ================================
        with tab2:
            df_plot = signal_result['df_with_indicators'].copy()
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.04,
                row_heights=[0.6, 0.2, 0.2],
                subplot_titles=["PRICE · BOLLINGER BANDS · MOVING AVERAGES", "RSI", "MACD"]
            )

            fig.add_trace(go.Candlestick(
                x=df_plot.index,
                open=df_plot['Open'], high=df_plot['High'],
                low=df_plot['Low'], close=df_plot['Close'],
                name="PRICE",
                increasing_line_color='#00ff64',
                decreasing_line_color='#ff0040',
                increasing_fillcolor='#003320',
                decreasing_fillcolor='#330010'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA20'],
                name="MA20", line=dict(color='#4facfe', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA50'],
                name="MA50", line=dict(color='#ffd200', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_Upper'],
                name="BB UPPER", line=dict(color='#a78bfa', width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_Lower'],
                name="BB LOWER", line=dict(color='#a78bfa', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(167,139,250,0.04)'), row=1, col=1)

            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'],
                name="RSI", line=dict(color='#00d4aa', width=1.5)), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ff0040", line_width=1, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00ff64", line_width=1, row=2, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="rgba(255,210,0,0.02)", row=2, col=1)

            hist_colors = ['#00ff64' if v >= 0 else '#ff0040'
                          for v in df_plot['MACD_Hist'].fillna(0)]
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACD_Hist'],
                name="HISTOGRAM", marker_color=hist_colors, opacity=0.7), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'],
                name="MACD", line=dict(color='#4facfe', width=1.5)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD_Signal'],
                name="SIGNAL", line=dict(color='#ffd200', width=1.5)), row=3, col=1)

            fig.update_layout(
                height=750,
                paper_bgcolor='#000510',
                plot_bgcolor='#000d1a',
                font=dict(color='#4a6080', family='Share Tech Mono'),
                legend=dict(bgcolor='#000d1a', bordercolor='#0a2040',
                           font=dict(size=10, color='#4a6080')),
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            for i in range(1, 4):
                fig.update_xaxes(gridcolor='#050f1a', showgrid=True, row=i, col=1)
                fig.update_yaxes(gridcolor='#050f1a', showgrid=True, row=i, col=1)

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # TAB 3 — FORECAST
        # ================================
        with tab3:
            last_30 = df_full[['Close']].tail(30)
            fig2 = go.Figure()

            fig2.add_trace(go.Scatter(
                x=last_30.index, y=last_30['Close'],
                name="HISTORICAL",
                line=dict(color='#4facfe', width=2),
                mode='lines+markers',
                marker=dict(size=3)
            ))

            pred_std = future_df['Predicted_Price'].std() * 0.8
            fig2.add_trace(go.Scatter(
                x=list(future_df.index) + list(future_df.index[::-1]),
                y=list(future_df['Predicted_Price'] + pred_std) +
                  list((future_df['Predicted_Price'] - pred_std))[::-1],
                fill='toself',
                fillcolor='rgba(0,212,170,0.08)',
                line=dict(color='rgba(0,0,0,0)'),
                name='CONFIDENCE BAND'
            ))

            fig2.add_trace(go.Scatter(
                x=future_df.index,
                y=future_df['Predicted_Price'],
                name="LSTM FORECAST",
                line=dict(color='#00d4aa', width=3),
                mode='lines+markers',
                marker=dict(size=10, symbol='diamond',
                           color='#00d4aa',
                           line=dict(color='#000510', width=2))
            ))

            fig2.add_trace(go.Scatter(
                x=[last_30.index[-1], future_df.index[0]],
                y=[last_30['Close'].iloc[-1], future_df['Predicted_Price'].iloc[0]],
                line=dict(color='#00d4aa', width=2, dash='dot'),
                showlegend=False
            ))

            fig2.update_layout(
                height=500,
                paper_bgcolor='#000510',
                plot_bgcolor='#000d1a',
                font=dict(color='#4a6080', family='Share Tech Mono'),
                legend=dict(bgcolor='#000d1a', bordercolor='#0a2040'),
                margin=dict(l=10, r=10, t=20, b=10)
            )
            fig2.update_xaxes(gridcolor='#050f1a')
            fig2.update_yaxes(gridcolor='#050f1a')
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<p class="section-header">7-DAY PRICE FORECAST</p>', unsafe_allow_html=True)
            pred_cols = st.columns(7)
            for i, (date, row) in enumerate(future_df.iterrows()):
                price = row['Predicted_Price']
                chg = ((price - current_price) / current_price) * 100
                color = "#00ff64" if chg >= 0 else "#ff0040"
                arrow = "▲" if chg >= 0 else "▼"
                with pred_cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#0a2040;font-size:0.65rem;font-family:'Share Tech Mono',monospace">
                            {date.strftime('%b %d')}
                        </div>
                        <div style="color:white;font-weight:700;font-size:0.95rem;font-family:'Share Tech Mono',monospace">
                            ${price:,.0f}
                        </div>
                        <div style="color:{color};font-size:0.8rem;font-family:'Share Tech Mono',monospace">
                            {arrow}{abs(chg):.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ================================
        # TAB 4 — FEAR & GREED
        # ================================
        with tab4:
            fg_left, fg_right = st.columns([1, 1])

            with fg_left:
                st.markdown('<p class="section-header">MARKET FEAR & GREED INDEX</p>', unsafe_allow_html=True)

                fig_fg = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=fear_score,
                    domain={'x': [0,1], 'y': [0,1]},
                    title={'text': f"<b>{fear_label}</b>",
                           'font': {'color': fear_color, 'size': 18, 'family': 'Orbitron'}},
                    number={'font': {'color': fear_color, 'size': 60,
                                    'family': 'Orbitron'}, 'suffix': ''},
                    gauge={
                        'axis': {
                            'range': [0, 100],
                            'tickvals': [0, 25, 50, 75, 100],
                            'ticktext': ['FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'GREED'],
                            'tickcolor': '#0a2040',
                            'tickfont': {'color': '#0a2040', 'size': 10}
                        },
                        'bar': {'color': fear_color, 'thickness': 0.3},
                        'bgcolor': '#000d1a',
                        'borderwidth': 1,
                        'bordercolor': '#0a2040',
                        'steps': [
                            {'range': [0, 25], 'color': '#1a0005'},
                            {'range': [25, 45], 'color': '#1a0a00'},
                            {'range': [45, 55], 'color': '#0a0a00'},
                            {'range': [55, 75], 'color': '#001a05'},
                            {'range': [75, 100], 'color': '#001a00'},
                        ],
                        'threshold': {
                            'line': {'color': fear_color, 'width': 4},
                            'thickness': 0.9,
                            'value': fear_score
                        }
                    }
                ))
                fig_fg.update_layout(
                    height=350,
                    paper_bgcolor='#000510',
                    font=dict(color='white'),
                    margin=dict(l=30, r=30, t=60, b=10)
                )
                st.plotly_chart(fig_fg, use_container_width=True)

            with fg_right:
                st.markdown('<p class="section-header">INDEX COMPONENTS</p>', unsafe_allow_html=True)

                components = [
                    ("RSI Momentum", min(100, max(0, (100 - signal_result['rsi']) * 1.2)), "#4facfe"),
                    ("Price Trend", 70 if signal_result['ma20'] > signal_result['ma50'] else 30, "#00d4aa"),
                    ("MACD Signal", 75 if signal_result['macd'] > 0 else 25, "#a78bfa"),
                    ("Volatility Index", max(0, 100 - df['Close'].pct_change().std() * 2000), "#ffd200"),
                    ("Volume Momentum", min(100, df['Volume'].iloc[-1] / df['Volume'].mean() * 50), "#f97316"),
                ]

                for comp_name, comp_val, comp_color in components:
                    comp_val = max(0, min(100, comp_val))
                    st.markdown(f"""
                    <div style="margin:0.6rem 0">
                        <div style="display:flex;justify-content:space-between;
                             font-family:'Share Tech Mono',monospace;font-size:0.8rem;
                             color:#0a2040;margin-bottom:0.3rem">
                            <span>{comp_name}</span>
                            <span style="color:{comp_color}">{comp_val:.0f}</span>
                        </div>
                        <div style="background:#000d1a;border-radius:2px;height:6px;
                             border:1px solid #050f1a">
                            <div style="background:{comp_color};height:100%;
                                 width:{comp_val}%;border-radius:2px;
                                 box-shadow:0 0 8px {comp_color}44;
                                 transition:width 0.5s ease">
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<p class="section-header">HOW TO READ THIS</p>', unsafe_allow_html=True)
                for label, rng, col in [
                    ("EXTREME FEAR (0-24)", "Deep oversold — potential BUY opportunity", "#ff0040"),
                    ("FEAR (25-44)", "Bearish sentiment dominating market", "#ff8c00"),
                    ("NEUTRAL (45-55)", "Balanced market forces", "#ffd200"),
                    ("GREED (56-74)", "Bullish momentum building", "#96c93d"),
                    ("EXTREME GREED (75-100)", "Overbought — exercise caution", "#00ff64"),
                ]:
                    st.markdown(f"""
                    <div class="indicator-row">
                        <span style="color:{col};font-weight:700">{label}</span>
                        <span style="color:#1a3a5c"> — {rng}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # ================================
        # TAB 5 — NEWS SENTIMENT
        # ================================
        with tab5:
            n_left, n_right = st.columns([2, 1])

            with n_left:
                st.markdown('<p class="section-header">LATEST NEWS & SENTIMENT</p>', unsafe_allow_html=True)

                for item in news_items:
                    sent_class = (
                        "news-sentiment-pos" if item['sentiment'] == 'positive'
                        else "news-sentiment-neg" if item['sentiment'] == 'negative'
                        else "news-sentiment-neu"
                    )
                    bar_color = (
                        "#00ff64" if item['sentiment'] == 'positive'
                        else "#ff0040" if item['sentiment'] == 'negative'
                        else "#ffd200"
                    )
                    bar_width = item['score'] * 100

                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">{item['emoji']} {item['headline']}</div>
                        <div style="margin-top:0.5rem;background:#050a14;border-radius:2px;height:4px">
                            <div style="background:{bar_color};height:100%;
                                 width:{bar_width:.0f}%;border-radius:2px;
                                 box-shadow:0 0 6px {bar_color}66"></div>
                        </div>
                        <div class="news-meta">
                            SENTIMENT SCORE:
                            <span class="{sent_class}">{item['score']:.2f}</span>
                            &nbsp;·&nbsp;{item['sentiment'].upper()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with n_right:
                st.markdown('<p class="section-header">SENTIMENT SUMMARY</p>', unsafe_allow_html=True)

                sent_pct = overall_sentiment * 100
                sent_color = "#00ff64" if sent_pct > 60 else "#ff0040" if sent_pct < 40 else "#ffd200"
                sent_label = "BULLISH" if sent_pct > 60 else "BEARISH" if sent_pct < 40 else "NEUTRAL"

                st.markdown(f"""
                <div style="text-align:center;padding:2rem;background:#000d1a;
                     border:1px solid #0a2040;border-radius:8px;
                     border-top:3px solid {sent_color}">
                    <div style="font-family:'Orbitron',monospace;color:{sent_color};
                         font-size:2rem;font-weight:900">{sent_pct:.0f}</div>
                    <div style="font-family:'Orbitron',monospace;color:{sent_color};
                         font-size:1.2rem;margin-top:0.3rem">{sent_label}</div>
                    <div style="color:#0a2040;font-size:0.75rem;font-family:'Share Tech Mono',monospace;
                         margin-top:0.5rem">OVERALL SENTIMENT SCORE</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                pos = sum(1 for i in news_items if i['sentiment'] == 'positive')
                neg = sum(1 for i in news_items if i['sentiment'] == 'negative')
                neu = sum(1 for i in news_items if i['sentiment'] == 'neutral')

                fig_pie = go.Figure(go.Pie(
                    labels=['POSITIVE', 'NEGATIVE', 'NEUTRAL'],
                    values=[pos, neg, neu],
                    marker_colors=['#00ff64', '#ff0040', '#ffd200'],
                    hole=0.6,
                    textfont=dict(family='Share Tech Mono', size=10),
                ))
                fig_pie.update_layout(
                    height=250,
                    paper_bgcolor='#000510',
                    font=dict(color='#4a6080'),
                    legend=dict(bgcolor='#000d1a', font=dict(size=9)),
                    margin=dict(l=10, r=10, t=10, b=10),
                    annotations=[dict(
                        text=f'<b>{sent_label}</b>',
                        x=0.5, y=0.5,
                        font=dict(size=12, color=sent_color, family='Orbitron'),
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # ================================
        # TAB 6 — LEADERBOARD
        # ================================
        with tab6:
            st.markdown('<p class="section-header">LIVE MARKET LEADERBOARD</p>', unsafe_allow_html=True)

            with st.spinner("📡 Fetching live market data..."):
                leaderboard = get_leaderboard()

            if leaderboard:
                medals = ["🥇", "🥈", "🥉"]
                for i, asset in enumerate(leaderboard):
                    rank = i + 1
                    chg = asset['change_pct']
                    chg_color = "#00ff64" if chg >= 0 else "#ff0040"
                    arrow = "▲" if chg >= 0 else "▼"
                    rank_display = medals[i] if i < 3 else str(rank)
                    is_crypto = "-USD" in asset['symbol']
                    type_badge = "₿ CRYPTO" if is_crypto else "📈 STOCK"
                    type_color = "#f97316" if is_crypto else "#4facfe"

                    st.markdown(f"""
                    <div class="leader-row">
                        <div style="font-family:'Orbitron',monospace;font-size:1.2rem;
                             width:40px;text-align:center">{rank_display}</div>
                        <div style="flex:1;margin-left:1rem">
                            <div style="color:white;font-weight:700;font-size:1rem">
                                {asset['name']}
                                <span style="color:{type_color};font-size:0.7rem;
                                      font-family:'Share Tech Mono',monospace;
                                      margin-left:0.5rem">{type_badge}</span>
                            </div>
                            <div style="color:#0a2040;font-size:0.8rem;
                                 font-family:'Share Tech Mono',monospace">
                                {asset['symbol']}
                            </div>
                        </div>
                        <div style="text-align:right">
                            <div style="color:white;font-family:'Share Tech Mono',monospace;
                                 font-weight:700">${asset['price']:,.2f}</div>
                            <div style="color:{chg_color};font-family:'Orbitron',monospace;
                                 font-size:0.9rem;font-weight:700">
                                {arrow} {abs(chg):.2f}%
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📡 Loading market data...")

else:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem">
        <div style="font-family:'Orbitron',monospace;font-size:4rem;
             color:#050f1a;letter-spacing:4px">⚡</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.3rem;
             color:#0a2040;margin-top:1rem;letter-spacing:3px">
            SELECT AN ASSET AND CLICK ANALYSE
        </div>
        <div style="font-family:'Share Tech Mono',monospace;color:#050f1a;
             margin-top:0.5rem;font-size:0.85rem">
            > awaiting input_
        </div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer">
    ⚡ QUANTAI TERMINAL · LSTM DEEP LEARNING · TECHNICAL ANALYSIS · YAHOO FINANCE DATA<br>
    BUILT BY <strong style="color:#00d4aa">RISHIT PANDYA</strong> ·
    MASTER OF DATA SCIENCE · UNIVERSITY OF ADELAIDE<br>
    <span style="color:#050f1a">⚠ NOT FINANCIAL ADVICE · EDUCATIONAL USE ONLY</span>
</div>
""", unsafe_allow_html=True)