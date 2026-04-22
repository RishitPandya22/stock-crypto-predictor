import yfinance as yf
import pandas as pd
import os

# ================================
# SYMBOLS WE SUPPORT
# ================================
STOCKS = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Google": "GOOGL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA"
}

CRYPTO = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "Dogecoin": "DOGE-USD",
    "BNB": "BNB-USD"
}

ALL_SYMBOLS = {**STOCKS, **CRYPTO}

# ================================
# FETCH DATA FUNCTION
# ================================
def fetch_data(symbol, period="1y"):
    """
    Fetch historical price data for a stock or crypto.
    period options: 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    print(f"Fetching data for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)

    if df.empty:
        print(f"No data found for {symbol}")
        return None

    # Keep only useful columns
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)  # remove timezone

    print(f"✅ Got {len(df)} days of data for {symbol}")
    print(df.tail())
    return df

# ================================
# TEST IT
# ================================
if __name__ == "__main__":
    # Test with Apple stock
    df_apple = fetch_data("AAPL", period="1y")

    # Test with Bitcoin
    df_btc = fetch_data("BTC-USD", period="1y")

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    if df_apple is not None:
        df_apple.to_csv("data/AAPL.csv")
        print("\n✅ Apple data saved!")

    if df_btc is not None:
        df_btc.to_csv("data/BTC-USD.csv")
        print("✅ Bitcoin data saved!")

    print("\n🎉 Stage 1 Complete!")