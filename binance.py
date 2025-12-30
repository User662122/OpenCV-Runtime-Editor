import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

# ===============================
# DATA DOWNLOAD
# ===============================
df = yf.download(
    "BTC-USD",
    period="3y",
    interval="1d",
    auto_adjust=False,
    progress=False
)

# FIX: Flatten MultiIndex columns from yfinance
df.columns = df.columns.get_level_values(0)

df.dropna(inplace=True)
df.index = pd.to_datetime(df.index)

# ===============================
# FEATURE ENGINEERING (NO LEAKAGE)
# ===============================
df["Prev_Close"]  = df["Close"].shift(1)
df["Prev_High"]   = df["High"].shift(1)
df["Prev_Low"]    = df["Low"].shift(1)
df["Prev_Volume"] = df["Volume"].shift(1)

df["Return"] = df["Close"].pct_change()

df["MA_5"]       = df["Close"].rolling(5).mean().shift(1)
df["MA_10"]      = df["Close"].rolling(10).mean().shift(1)
df["MA_20"]      = df["Close"].rolling(20).mean().shift(1)
df["Volatility"] = df["Return"].rolling(10).std().shift(1)

# ===============================
# TARGET: NEXT DAY UP / DOWN
# ===============================
df["Target"] = (df["Close"].shift(-1) > df["Open"].shift(-1)).astype(int)
df.dropna(inplace=True)

features = [
    "Open", "Prev_Close", "Prev_High", "Prev_Low", "Prev_Volume",
    "MA_5", "MA_10", "MA_20", "Volatility"
]

X = df[features]
y = df["Target"]

# ===============================
# SCALING + MODEL TRAINING
# ===============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_scaled, y)

# ===============================
# LIVE INPUT (TRUE DAY START OPEN)
# ===============================
today_1m = yf.download(
    "BTC-USD",
    period="1d",
    interval="1m",
    progress=False
)

today_1m.columns = today_1m.columns.get_level_values(0)

# ✅ TRUE DAY OPEN (FIRST MINUTE)
live_open_price = float(today_1m["Open"].iloc[0])

# ===============================
# LIVE FEATURE CREATION
# ===============================
last_row = df.iloc[-1]

live_features = pd.DataFrame([{
    "Open": live_open_price,
    "Prev_Close": last_row["Close"],
    "Prev_High": last_row["High"],
    "Prev_Low": last_row["Low"],
    "Prev_Volume": last_row["Volume"],
    "MA_5": last_row["MA_5"],
    "MA_10": last_row["MA_10"],
    "MA_20": last_row["MA_20"],
    "Volatility": last_row["Volatility"]
}])

# ===============================
# LIVE PREDICTION (NEXT DAY)
# ===============================
live_scaled = scaler.transform(live_features.values)

proba = model.predict_proba(live_scaled)[0]
prediction = np.argmax(proba)

direction = "UP (LONG)" if prediction == 1 else "DOWN (SHORT)"
confidence = round(np.max(proba) * 100, 2)

print("\n===== LIVE NEXT DAY PREDICTION =====")
print(f"Today's TRUE Day-Start Open Price: ${live_open_price:,.2f}")
print(f"Tomorrow Direction: {direction}")
print(f"Confidence: {confidence}%")