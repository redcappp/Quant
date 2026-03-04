import yfinance as yf
import pandas as pd
import numpy as np

ticker="SPY"
print(f"Downloading data for {ticker}...")

data=yf.download(ticker,period="5y")

data=data[["Close"]].copy()

data["daily_return"]=data["Close"].pct_change()

data.dropna(inplace=True)

daily_volatility=data["daily_return"].std()

annual_volatility=daily_volatility*np.sqrt(252)

print("----# Risk Metric #----")
print(f"Daily Volatility: {daily_volatility:.4f} ({daily_volatility * 100:.2f}%)")
print(f"Annualized Volatility: {annual_volatility:.4f} ({annual_volatility * 100:.2f}%)")

print("\n--- Recent Data ---")
print(data.tail())