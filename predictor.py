import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler

# ================================
# SYMBOLS
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
# FETCH DATA
# ================================
def fetch_data(symbol, period="2y"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    if df.empty:
        return None
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)
    return df

# ================================
# CREATE FEATURES FOR ML
# ================================
def create_features(df):
    df = df.copy()

    # Lag features — past prices as inputs
    for lag in [1, 2, 3, 5, 10, 20]:
        df[f'lag_{lag}'] = df['Close'].shift(lag)

    # Rolling stats
    df['rolling_mean_5']  = df['Close'].rolling(5).mean()
    df['rolling_mean_20'] = df['Close'].rolling(20).mean()
    df['rolling_std_5']   = df['Close'].rolling(5).std()
    df['rolling_std_20']  = df['Close'].rolling(20).std()

    # Price momentum
    df['momentum_5']  = df['Close'] / df['Close'].shift(5) - 1
    df['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1

    # Volume momentum
    df['vol_momentum'] = df['Volume'] / df['Volume'].rolling(10).mean()

    # High-Low range
    df['hl_range'] = (df['High'] - df['Low']) / df['Close']

    df = df.dropna()
    return df

# ================================
# TRAIN MODEL
# ================================
def train_model(symbol, period="2y"):
    print(f"Fetching data for {symbol}...")
    df = fetch_data(symbol, period)
    if df is None:
        return None, None, None, None

    print(f"✅ Got {len(df)} days of data")
    df_feat = create_features(df)

    feature_cols = [c for c in df_feat.columns if c != 'Close'
                    and c not in ['Open','High','Low','Volume']]

    X = df_feat[feature_cols].values
    y = df_feat['Close'].values

    # Scale
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1,1)).ravel()

    # Train/test split
    split = int(len(X_scaled) * 0.8)
    X_train = X_scaled[:split]
    y_train = y_scaled[:split]

    print("🚀 Training Gradient Boosting model...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )
    model.fit(X_train, y_train)
    print("✅ Model trained!")

    return model, (scaler_X, scaler_y), df, feature_cols

# ================================
# PREDICT NEXT 7 DAYS
# ================================
def predict_future(model, scalers, df, feature_cols, days=7):
    scaler_X, scaler_y = scalers

    df_feat = create_features(df)
    last_row = df_feat[feature_cols].iloc[-1].values

    predictions = []
    current_features = last_row.copy()
    current_price = df['Close'].iloc[-1]

    for i in range(days):
        X_input = scaler_X.transform(current_features.reshape(1, -1))
        pred_scaled = model.predict(X_input)[0]
        pred_price = scaler_y.inverse_transform([[pred_scaled]])[0][0]

        # Add small random walk for realism
        noise = np.random.normal(0, current_price * 0.005)
        pred_price = pred_price + noise
        predictions.append(pred_price)

        # Update lag features for next prediction
        current_features[0] = pred_price  # lag_1
        current_price = pred_price

    last_date = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=days,
        freq='B'
    )

    future_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Price': predictions
    }).set_index('Date')

    return future_df

# ================================
# TEST
# ================================
if __name__ == "__main__":
    model, scalers, df, feature_cols = train_model("AAPL")
    if model:
        future = predict_future(model, scalers, df, feature_cols)
        print("\n📅 Next 7 Day Predictions:")
        print(future)
        print("\n🎉 Done!")