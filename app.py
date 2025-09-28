from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/rsi")
def get_rsi(symbol: str, period: int = 14):
    # Download last 2 months of daily stock prices
    data = yf.download(symbol, period="2mo", interval="1d")
    if data.empty:
        return {"symbol": symbol, "rsi": None, "error": "No data found"}
    
    data['Change'] = data['Close'].diff()
    data['Gain'] = data['Change'].apply(lambda x: x if x > 0 else 0)
    data['Loss'] = data['Change'].apply(lambda x: -x if x < 0 else 0)
    data['AvgGain'] = data['Gain'].rolling(window=period).mean()
    data['AvgLoss'] = data['Loss'].rolling(window=period).mean()
    data['RS'] = data['AvgGain'] / data['AvgLoss']
    data['RSI'] = 100 - (100 / (1 + data['RS']))
    
    rsi_value = data['RSI'].iloc[-1]
    return {"symbol": symbol, "rsi": float(rsi_value)}
