from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv

# Carga la configuración y MongoDB (igual que en tu app.py)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Copia aquí todas tus funciones existentes:
def get_crypto_data():
    collection = db["cryptos"]
    data = list(collection.find())
    if not data:
        return pd.DataFrame()

    rows = []
    for doc in data:
        try:
            price = float(str(doc.get("price", "0")).replace("$", "").replace(",", ""))
        except:
            price = 0.0

        date = doc.get("scraped_at")
        if isinstance(date, dict) and "$date" in date:
            date = pd.to_datetime(date["$date"])
        else:
            try:
                date = pd.to_datetime(date)
            except:
                date = None

        if date:
            rows.append({
                "name": doc.get("name", ""),
                "symbol": doc.get("symbol", ""),
                "price": price,
                "scraped_at": date
            })

    df = pd.DataFrame(rows)
    return df

def entrenar_modelo(data, window=10):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))

    X, y = [], []
    for i in range(window, len(scaled_data)):
        X.append(scaled_data[i-window:i])
        y.append(scaled_data[i])

    if len(X) == 0:
        raise ValueError("Datos insuficientes para crear ventanas de entrenamiento")

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    return model, scaler

def predecir_precio(model, scaler, data, window=10):
    last_window = data[-window:]
    scaled_last_window = scaler.transform(last_window.reshape(-1, 1))
    X_test = np.reshape(scaled_last_window, (1, window, 1))
    scaled_pred = model.predict(X_test)
    pred = scaler.inverse_transform(scaled_pred)
    return pred[0][0]

# get_crypto_data(), entrenar_modelo(), predecir_precio()

@app.post("/option")
async def get_best_prediction():
    df = get_crypto_data()
    if df.empty:
        return {"error": "No data available"}

    df["date"] = df["scraped_at"].dt.date
    tabla_diaria = df.groupby(["date", "symbol"]).agg({"price": "mean"}).reset_index()

    WINDOW_SIZE = 10
    predictions = []

    for symbol in df["symbol"].unique():
        datos_symbol = tabla_diaria[tabla_diaria["symbol"] == symbol].sort_values("date")
        precios = datos_symbol["price"].values

        if len(precios) > WINDOW_SIZE:
            try:
                model, scaler = entrenar_modelo(precios, WINDOW_SIZE)
                pred = predecir_precio(model, scaler, precios, WINDOW_SIZE)
                change = (pred - precios[-1]) / precios[-1] * 100
                predictions.append({
                    "symbol": symbol,
                    "prediction": float(pred),
                    "change_percent": float(change)
                })
            except Exception as e:
                continue

    if not predictions:
        return {"error": "Could not generate predictions"}

    best = max(predictions, key=lambda x: x["change_percent"])
    return {
        "best_crypto": best["symbol"]
    }
