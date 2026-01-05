import time
from datetime import datetime, timezone, timedelta
import requests

TARGET_SECOND = 3  # 00:00:04 UTC

# -----------------------------
# FETCH BINANCE SERVER TIME
# -----------------------------
try:
    r = requests.get("https://fapi.binance.com/fapi/v1/time", timeout=5)
    r.raise_for_status()
    server_time_ms = r.json()['serverTime']
except Exception as e:
    raise Exception(f"Error fetching Binance time: {e}")

# Convert to datetime UTC
server_time = datetime.fromtimestamp(server_time_ms / 1000, tz=timezone.utc)

# Next 00:00:04 UTC
target_time = datetime(
    server_time.year, server_time.month, server_time.day,
    3, 56, TARGET_SECOND, tzinfo=timezone.utc
)
if server_time >= target_time:
    # If already past, move to next day
    target_time += timedelta(days=1)

# Calculate remaining seconds
seconds_to_wait = (target_time - server_time).total_seconds()

print(f"⏳ Binance UTC now: {server_time.strftime('%H:%M:%S')}")
print(f"⏳ Waiting {seconds_to_wait:.2f} seconds until 00:00:04 UTC...")

# Single sleep until target
time.sleep(seconds_to_wait)

print(f"🎯 It's {TARGET_SECOND} sec past 00:00 UTC on Binance! Script starting...\n")

# -----------------------------
# YOUR SCRIPT STARTS HERE
# -----------------------------
# yahan aapka prediction / trading code rakh sakte ho
print("🚀 Script execution started!")
import requests
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

#===============================
# DATA DOWNLOAD (BINANCE VISION) - LAST ~1000 DAYS
#===============================

def fetch_binance_data(symbol="BTCUSDT", interval="1d", limit=1000):
    url = "https://data-api.binance.vision/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        cols = [
            "Open Time", "Open", "High", "Low", "Close", "Volume",
            "Close Time", "Quote Asset Volume", "Number of Trades",
            "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
        ]
        df = pd.DataFrame(data, columns=cols)
        df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
        df.set_index("Date", inplace=True)
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, axis=1)
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception as e:
        print(f"Error fetching data from Binance: {e}")
        return pd.DataFrame()

df = fetch_binance_data(symbol="BTCUSDT", interval="1d", limit=1000)

if df.empty:
    print("Data fetch failed. Aborting.")
    exit()

df.dropna(inplace=True)

#===============================
# FEATURE ENGINEERING (NO LEAKAGE)
#===============================

df["Prev_Close"]  = df["Close"].shift(1)
df["Prev_High"]   = df["High"].shift(1)
df["Prev_Low"]    = df["Low"].shift(1)
df["Prev_Volume"] = df["Volume"].shift(1)

df["Return"] = df["Close"].pct_change()

df["MA_5"]       = df["Close"].rolling(5).mean().shift(1)
df["MA_10"]      = df["Close"].rolling(10).mean().shift(1)
df["MA_20"]      = df["Close"].rolling(20).mean().shift(1)
df["Volatility"] = df["Return"].rolling(10).std().shift(1)

#===============================
# TARGET: NEXT DAY UP / DOWN (ONLY FOR TRAINING)
#===============================

df["Target"] = (df["Close"].shift(-1) > df["Open"].shift(-1)).astype(int)

df.dropna(inplace=True)

features = [
    "Open", "Prev_Close", "Prev_High", "Prev_Low", "Prev_Volume",
    "MA_5", "MA_10", "MA_20", "Volatility"
]

target = "Target"

#===============================
# TRAIN MODEL ON LAST 2 MONTHS (~60 DAYS)
#===============================

training_days = 60  # last 2 months

train_start = max(0, len(df) - 1 - training_days)
train_df = df.iloc[train_start:-1]  # Last 60 days for training

X_train = train_df[features]
y_train = train_df[target]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train_scaled, y_train)

#===============================
# PREDICT FOR TODAY (LATEST DAY IN DATA)
#===============================

today_row = df.iloc[-1]  # Latest complete day candle

X_today = today_row[features].values.reshape(1, -1)
X_today_scaled = scaler.transform(X_today)

probas = model.predict_proba(X_today_scaled)[0]
prediction = np.argmax(probas)
confidence_pct = np.max(probas) * 100

direction = "UP (LONG)" if prediction == 1 else "DOWN (SHORT)"

today_date = today_row.name.strftime("%Y-%m-%d")
today_open = round(today_row["Open"], 2)

print("\n===== LIVE PREDICTION FOR TODAY =====\n")
print(f"Date: {today_date}")
print(f"Today's Open Price: ${today_open}")
print(f"Model Prediction: {direction}")
print(f"Confidence: {round(confidence_pct, 2)}%")
print("\nNote: This predicts if today's close > today's open (UP) or not (DOWN).")
print("Model trained on previous 60 days' data, same logic as your backtest.")