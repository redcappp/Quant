import yfinance as yf
import pandas as pd
import numpy as np

ticker = "SPY"
print(f"Downloading data for {ticker}...")
data = yf.download(ticker, period="5y")

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data = data[['Close']].copy()

data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()


data['Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)

data['Position'] = data['Signal'].shift(1)

data.dropna(inplace=True)

print("\n--- Latest Trading Data & Signals ---")

print(data[['Close', 'SMA_50', 'SMA_200', 'Signal', 'Position']].tail(10))