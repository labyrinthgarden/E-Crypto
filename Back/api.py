from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "e_trading")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://192.168.1.10:3000",
        "http://192.168.1.22:3000",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["*"],
)

# Request model
class MessageRequest(BaseModel):
    message: str

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

def get_best_prediction():
    df = get_crypto_data()
    if df.empty:
        return "No hay datos disponibles para hacer predicciones."

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
                    "current_price": float(precios[-1]),
                    "change_percent": float(change)
                })
            except Exception as e:
                continue

    if not predictions:
        return "No se pudieron generar predicciones con los datos actuales."

    best = max(predictions, key=lambda x: x["change_percent"])
    worst = min(predictions, key=lambda x: x["change_percent"])

    return f"🚀 Mi mejor predicción actual es {best['symbol']} con un potencial de subida del {best['change_percent']:.2f}%. Precio actual: ${best['current_price']:.2f}, predicción: ${best['prediction']:.2f}. También vigila {worst['symbol']} que podría bajar {abs(worst['change_percent']):.2f}%."

def get_4_month_recommendation():
    df = get_crypto_data()
    if df.empty:
        return "No hay suficientes datos históricos para analizar los últimos 4 meses."

    four_months_ago = datetime.now() - timedelta(days=120)
    df_recent = df[df["scraped_at"] >= four_months_ago]

    if df_recent.empty:
        return "No hay datos de los últimos 4 meses disponibles."

    df_recent["date"] = df_recent["scraped_at"].dt.date
    monthly_data = df_recent.groupby(["symbol"]).agg({
        "price": ["mean", "std", "min", "max"]
    }).reset_index()

    analysis = []
    for _, row in monthly_data.iterrows():
        symbol = row["symbol"]
        avg_price = row[("price", "mean")]
        volatility = row[("price", "std")] / avg_price * 100
        analysis.append({
            "symbol": symbol,
            "avg_price": avg_price,
            "volatility": volatility
        })

    stable_crypto = min(analysis, key=lambda x: x["volatility"])
    volatile_crypto = max(analysis, key=lambda x: x["volatility"])

    return f"📊 Basándome en los últimos 4 meses: {stable_crypto['symbol']} ha sido la más estable (volatilidad: {stable_crypto['volatility']:.1f}%) - ideal para inversiones conservadoras. {volatile_crypto['symbol']} ha sido muy volátil ({volatile_crypto['volatility']:.1f}%) - mayor riesgo pero potencial de ganancias altas."

def get_long_term_recommendation():
    df = get_crypto_data()
    if df.empty:
        return "No hay datos suficientes para recomendaciones a largo plazo."

    df["date"] = df["scraped_at"].dt.date
    symbols_data = df.groupby("symbol").agg({
        "price": ["count", "mean", "std"]
    }).reset_index()

    # Find crypto with most data points (more historical data)
    best_data = symbols_data.loc[symbols_data[("price", "count")].idxmax()]
    symbol_with_most_data = best_data["symbol"]

    return f"🔮 Para largo plazo, recomiendo diversificar tu portafolio. {symbol_with_most_data} tiene el historial más extenso en nuestros datos, lo que la hace más predecible. Para largo plazo siempre considera: 70% en Bitcoin/Ethereum (menos volátiles), 20% en altcoins prometedoras, y 10% en proyectos experimentales. ¡La paciencia es clave en cripto!"

def get_short_term_recommendation():
    df = get_crypto_data()
    if df.empty:
        return "No hay datos actuales para recomendaciones a corto plazo."

    # Get most recent prices
    recent_data = df.sort_values("scraped_at").groupby("symbol").tail(5)
    price_changes = []

    for symbol in recent_data["symbol"].unique():
        symbol_data = recent_data[recent_data["symbol"] == symbol].sort_values("scraped_at")
        if len(symbol_data) >= 2:
            recent_change = (symbol_data.iloc[-1]["price"] - symbol_data.iloc[0]["price"]) / symbol_data.iloc[0]["price"] * 100
            price_changes.append({
                "symbol": symbol,
                "change": recent_change,
                "current_price": symbol_data.iloc[-1]["price"]
            })

    if not price_changes:
        return "No hay suficientes datos recientes para análisis a corto plazo."

    trending_up = max(price_changes, key=lambda x: x["change"])
    trending_down = min(price_changes, key=lambda x: x["change"])

    return f"⚡ A corto plazo: {trending_up['symbol']} muestra tendencia alcista reciente (+{trending_up['change']:.2f}%) - podría ser buena para trading rápido. ¡Cuidado con {trending_down['symbol']} que está bajando ({trending_down['change']:.2f}%)! Para corto plazo: usa stop-loss, no inviertas más del 5% de tu capital, y estate atento a las noticias del mercado."

def get_current_prices():
    df = get_crypto_data()
    if df.empty:
        return "No hay cotizaciones disponibles en este momento."

    # Get latest prices for each crypto
    latest_prices = df.sort_values("scraped_at").groupby("symbol").tail(1)

    price_info = []
    for _, row in latest_prices.iterrows():
        price_info.append(f"{row['symbol']}: ${row['price']:,.2f}")

    current_time = datetime.now().strftime("%H:%M")
    prices_text = " | ".join(price_info)

    return f"💰 Cotizaciones actuales ({current_time}): {prices_text}. Los precios se actualizan constantemente según el mercado. Recuerda que la volatilidad es alta en cripto - estos precios pueden cambiar rápidamente."

@app.post("/option/")
async def handle_option(request: MessageRequest):
    message = request.message.lower()

    try:
        if "mejor prediccion" in message or "prediccion" in message:
            response = get_best_prediction()
        elif "4 meses" in message or "ultimos" in message and "meses" in message:
            response = get_4_month_recommendation()
        elif "largo plazo" in message:
            response = get_long_term_recommendation()
        elif "corto plazo" in message:
            response = get_short_term_recommendation()
        elif "cotizaciones" in message or "precios" in message:
            response = get_current_prices()
        else:
            response = "🤖 No entiendo tu pregunta. Puedes preguntarme sobre predicciones, recomendaciones a corto/largo plazo, o cotizaciones actuales."

        return {"response": response}

    except Exception as e:
        return {"response": f"❌ Ha ocurrido un error al procesar tu consulta: {str(e)}"}

@app.get("/")
async def root():
    return {"message": "E-Crypto API funcionando correctamente"}
