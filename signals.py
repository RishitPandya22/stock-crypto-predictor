import pandas as pd
import numpy as np

# ================================
# RSI — Relative Strength Index
# ================================
def calculate_rsi(df, period=14):
    """
    RSI > 70 = Overbought = possible SELL
    RSI < 30 = Oversold   = possible BUY
    RSI 30-70 = Neutral   = HOLD
    """
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ================================
# MOVING AVERAGES
# ================================
def calculate_moving_averages(df):
    """
    MA20 crosses above MA50 = BUY signal (golden cross)
    MA20 crosses below MA50 = SELL signal (death cross)
    """
    df = df.copy()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    return df

# ================================
# MACD
# ================================
def calculate_macd(df):
    """
    MACD line crosses above signal = BUY
    MACD line crosses below signal = SELL
    """
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# ================================
# BOLLINGER BANDS
# ================================
def calculate_bollinger_bands(df, period=20):
    """
    Price touches lower band = BUY
    Price touches upper band = SELL
    """
    df = df.copy()
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * std)
    df['BB_Lower'] = df['BB_Middle'] - (2 * std)
    return df

# ================================
# GENERATE FINAL SIGNAL
# ================================
def generate_signal(df):
    """
    Combines all indicators to give ONE final signal:
    BUY / SELL / HOLD with confidence score
    """
    df = df.copy()
    df = calculate_moving_averages(df)
    df = calculate_bollinger_bands(df)

    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df)

    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0  # positive = BUY, negative = SELL
    reasons = []

    # --- RSI Signal ---
    rsi_val = latest['RSI']
    if rsi_val < 30:
        score += 2
        reasons.append(f"✅ RSI {rsi_val:.1f} — Oversold (BUY signal)")
    elif rsi_val > 70:
        score -= 2
        reasons.append(f"🔴 RSI {rsi_val:.1f} — Overbought (SELL signal)")
    else:
        reasons.append(f"⚪ RSI {rsi_val:.1f} — Neutral")

    # --- Moving Average Signal ---
    if latest['MA20'] > latest['MA50']:
        score += 1
        reasons.append(f"✅ MA20 > MA50 — Bullish trend (BUY signal)")
    else:
        score -= 1
        reasons.append(f"🔴 MA20 < MA50 — Bearish trend (SELL signal)")

    # --- MA200 Signal (long term trend) ---
    if not pd.isna(latest['MA200']):
        if latest['Close'] > latest['MA200']:
            score += 1
            reasons.append(f"✅ Price above MA200 — Long term uptrend")
        else:
            score -= 1
            reasons.append(f"🔴 Price below MA200 — Long term downtrend")

    # --- MACD Signal ---
    if latest['MACD'] > latest['MACD_Signal']:
        score += 1
        reasons.append(f"✅ MACD bullish crossover (BUY signal)")
    else:
        score -= 1
        reasons.append(f"🔴 MACD bearish crossover (SELL signal)")

    # --- Bollinger Band Signal ---
    if latest['Close'] < latest['BB_Lower']:
        score += 2
        reasons.append(f"✅ Price below lower Bollinger Band (BUY signal)")
    elif latest['Close'] > latest['BB_Upper']:
        score -= 2
        reasons.append(f"🔴 Price above upper Bollinger Band (SELL signal)")
    else:
        reasons.append(f"⚪ Price within Bollinger Bands — Neutral")

    # --- Final Decision ---
    max_score = 7
    confidence = abs(score) / max_score * 100

    if score >= 2:
        signal = "BUY"
        emoji = "🟢"
    elif score <= -2:
        signal = "SELL"
        emoji = "🔴"
    else:
        signal = "HOLD"
        emoji = "🟡"

    return {
        "signal": signal,
        "emoji": emoji,
        "score": score,
        "confidence": round(confidence, 1),
        "reasons": reasons,
        "rsi": round(rsi_val, 2),
        "ma20": round(latest['MA20'], 2),
        "ma50": round(latest['MA50'], 2),
        "macd": round(latest['MACD'], 4),
        "current_price": round(latest['Close'], 2),
        "bb_upper": round(latest['BB_Upper'], 2),
        "bb_lower": round(latest['BB_Lower'], 2),
        "df_with_indicators": df
    }

# ================================
# TEST IT
# ================================
if __name__ == "__main__":
    from predictor import fetch_data

    print("Testing signals for AAPL...\n")
    df = fetch_data("AAPL", period="1y")
    result = generate_signal(df)

    print(f"Current Price: ${result['current_price']}")
    print(f"\n{'='*40}")
    print(f"  {result['emoji']} SIGNAL: {result['signal']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"{'='*40}")
    print(f"\n📊 Indicator Breakdown:")
    for reason in result['reasons']:
        print(f"  {reason}")

    print(f"\n🔢 Raw Values:")
    print(f"  RSI:    {result['rsi']}")
    print(f"  MA20:   ${result['ma20']}")
    print(f"  MA50:   ${result['ma50']}")
    print(f"  MACD:   {result['macd']}")

    print("\n🎉 Stage 3 Complete!")