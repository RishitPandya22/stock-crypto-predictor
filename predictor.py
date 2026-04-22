import yfinance as yf
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

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
# PREPARE DATA FOR LSTM
# ================================
def prepare_data(df, lookback=60):
    """
    lookback = how many past days the LSTM looks at
    to predict the next day
    """
    close_prices = df['Close'].values.reshape(-1, 1)

    # Scale prices to 0-1 range (LSTM works better this way)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(close_prices)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, 0])  # last 60 days
        y.append(scaled[i, 0])             # next day price

    X, y = np.array(X), np.array(y)

    # Reshape for LSTM: (samples, timesteps, features)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # 80% train, 20% test
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test, scaler, close_prices

# ================================
# BUILD LSTM MODEL
# ================================
def build_model(lookback=60):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(lookback, 1)),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# ================================
# TRAIN MODEL
# ================================
def train_model(symbol, period="2y"):
    print(f"\n🔄 Fetching data for {symbol}...")
    df = fetch_data(symbol, period)
    if df is None:
        print("❌ No data found!")
        return None, None, None, None

    print(f"✅ Got {len(df)} days of data")
    print("🧠 Preparing data for LSTM...")

    X_train, X_test, y_train, y_test, scaler, close_prices = prepare_data(df)

    print(f"📊 Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print("🚀 Training LSTM model (this takes 1-2 mins)...")

    model = build_model()

    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1
    )

    # Evaluate
    y_pred = model.predict(X_test, verbose=0)
    y_pred_actual = scaler.inverse_transform(y_pred)
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    mae = mean_absolute_error(y_test_actual, y_pred_actual)
    rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))

    print(f"\n📈 Model Performance:")
    print(f"   MAE  (avg error): ${mae:.2f}")
    print(f"   RMSE            : ${rmse:.2f}")

    return model, scaler, df, history

# ================================
# PREDICT NEXT 7 DAYS
# ================================
def predict_future(model, scaler, df, days=7):
    close_prices = df['Close'].values.reshape(-1, 1)
    scaled = scaler.transform(close_prices)

    # Use last 60 days as input
    last_60 = scaled[-60:]
    predictions = []

    current_input = last_60.copy()

    for _ in range(days):
        X_input = current_input[-60:].reshape(1, 60, 1)
        pred_scaled = model.predict(X_input, verbose=0)
        pred_price = scaler.inverse_transform(pred_scaled)[0][0]
        predictions.append(pred_price)

        # Add prediction to input for next step
        current_input = np.append(
            current_input,
            pred_scaled,
            axis=0
        )

    # Create future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=days,
        freq='B'  # Business days only
    )

    future_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Price': predictions
    }).set_index('Date')

    return future_df

# ================================
# TEST IT
# ================================
if __name__ == "__main__":
    # Train on Apple stock
    model, scaler, df, history = train_model("AAPL", period="2y")

    if model is not None:
        print("\n🔮 Predicting next 7 days...")
        future = predict_future(model, scaler, df, days=7)
        print("\n📅 Next 7 Day Price Predictions for AAPL:")
        print(future.to_string())
        print("\n🎉 Stage 2 Complete!")