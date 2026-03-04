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

# 2. Generate Signals (Your code from Task 2)
data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()
data['Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
data['Position'] = data['Signal'].shift(1)
data.dropna(inplace=True)

# --- THE NEW STUFF: CALCULATING PNL ---

# 3. Calculate Daily Returns
# Market Return: What SPY did that day
data['Market_Return'] = data['Close'].pct_change()

# Strategy Return: We only get the market return IF our Position was 1. If 0, we get 0.
data['Strategy_Return'] = data['Position'] * data['Market_Return']

# 4. Calculate Cumulative Wealth
# Assuming $1 invested, we track how it grows over the 5 years
data['Cumulative_Market'] = (1 + data['Market_Return']).cumprod()
data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()

# 5. Print Final Results
# .iloc[-1] grabs the very last row of the dataset
market_total = (data['Cumulative_Market'].iloc[-1] - 1) * 100
strategy_total = (data['Cumulative_Strategy'].iloc[-1] - 1) * 100

print(f"\n--- 5-Year Performance ---")
print(f"Buy & Hold Return:   {market_total:.2f}%")
print(f"SMA Strategy Return: {strategy_total:.2f}%")

# 6. Plot the Equity Curve
plt.figure(figsize=(10,6))
plt.plot(data.index, data['Cumulative_Market'], label='Buy & Hold SPY', color='blue', alpha=0.6)
plt.plot(data.index, data['Cumulative_Strategy'], label='SMA Strategy', color='orange', linewidth=2)
plt.title(f"Equity Curve: {ticker} - Buy & Hold vs. SMA Strategy")
plt.ylabel("Growth of $1")
plt.legend()
plt.grid(True)
plt.show()