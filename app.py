import yfinance as yf
from fastapi import FastAPI

app = FastAPI()

def calculate_rsi(symbol: str, period: int = 14):
    original_symbol = symbol.upper()

    # If no '.' present, assume NSE stock
    if "." not in symbol:
        symbol = original_symbol + ".NS"
    else:
        symbol = original_symbol

    data = yf.download(symbol, period="3mo", interval="1d")

    if data.empty:
        return {"symbol": original_symbol, "rsi": None, "error": "No data found for symbol"}

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return {"symbol": original_symbol, "rsi": round(rsi.iloc[-1], 2)}

@app.get("/rsi/{symbol}")
async def get_rsi(symbol: str):
    return calculate_rsi(symbol)
