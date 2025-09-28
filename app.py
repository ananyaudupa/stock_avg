from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yfinance as yf
import pandas as pd

app = FastAPI()

# Allow frontend to fetch data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/rsi")
def get_rsi(symbol: str, period: int = 14):
    try:
        clean_symbol = symbol.upper().strip()

        # If symbol does not already have exchange suffix → assume NSE
        if "." not in clean_symbol:
            yf_symbol = clean_symbol + ".NS"
        else:
            yf_symbol = clean_symbol

        data = yf.download(yf_symbol, period="2mo", interval="1d")

        if data.empty:
            return {"symbol": clean_symbol, "rsi": None, "error": "No data found for symbol"}

        data["Change"] = data["Close"].diff()
        data["Gain"] = data["Change"].apply(lambda x: x if x > 0 else 0)
        data["Loss"] = data["Change"].apply(lambda x: -x if x < 0 else 0)
        data["AvgGain"] = data["Gain"].rolling(window=period).mean()
        data["AvgLoss"] = data["Loss"].rolling(window=period).mean()
        data["RS"] = data["AvgGain"] / data["AvgLoss"]
        data["RSI"] = 100 - (100 / (1 + data["RS"]))

        rsi_value = data["RSI"].iloc[-1]
        if pd.isna(rsi_value):
            return {"symbol": clean_symbol, "rsi": None, "error": "Insufficient data to calculate RSI"}

        return {"symbol": clean_symbol, "rsi": float(rsi_value)}

    except Exception as e:
        return {"symbol": symbol, "rsi": None, "error": f"Error calculating RSI: {str(e)}"}
