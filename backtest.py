import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Fetch & Clean Data (Your code from Task 2)
ticker = "SPY"
print(f"Simulating trades for {ticker}...")
data = yf.download(ticker, period="5y")

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
data = data[['Close']].copy()


data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()
data['Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
data['Position'] = data['Signal'].shift(1)
data.dropna(inplace=True)

data['Market_Return'] = data['Close'].pct_change()
data['Strategy_Return_Gross'] = data['Position'] * data['Market_Return']

data['Trades'] = data['Position'].diff().abs()


transaction_cost = 0.001 

data['Strategy_Return_Net'] = data['Strategy_Return_Gross'] - (data['Trades'] * transaction_cost)

data['Cumulative_Market'] = (1 + data['Market_Return']).cumprod()
data['Cumulative_Strategy_Net'] = (1 + data['Strategy_Return_Net']).cumprod()

market_total = (data['Cumulative_Market'].iloc[-1] - 1) * 100
strategy_total = (data['Cumulative_Strategy_Net'].iloc[-1] - 1) * 100

print(f"\n--- 5-Year Performance (Net of Fees) ---")
print(f"Buy & Hold Return:   {market_total:.2f}%")
print(f"SMA Strategy Return: {strategy_total:.2f}%")

total_trades = data['Trades'].sum()
print(f"Total Trades Executed: {total_trades}")

plt.figure(figsize=(10,6))
plt.plot(data.index, data['Cumulative_Market'], label='Buy & Hold SPY', color='blue', alpha=0.6)
plt.plot(data.index, data['Cumulative_Strategy_Net'], label='SMA Strategy (Net)', color='orange', linewidth=2)
plt.title(f"Equity Curve (Net of Fees): {ticker} - Buy & Hold vs. SMA")
plt.ylabel("Growth of $1")
plt.legend()
plt.grid(True)
plt.show()