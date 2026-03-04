import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# 1. Fetch Data
tickers = ['GS', 'MS']
print(f"Running Pairs Backtest for {tickers[0]} and {tickers[1]}...")
data = yf.download(tickers, period="5y")
data = data['Close'].copy()
data.dropna(inplace=True)

# 2. Calculate Spread & Z-Score
x_with_constant = sm.add_constant(data['GS'])
model = sm.OLS(data['MS'], x_with_constant).fit()
hedge_ratio = model.params.iloc[1]

data['Spread'] = data['MS'] - (hedge_ratio * data['GS'])
spread_mean = data['Spread'].mean()
spread_std = data['Spread'].std()
data['Z_Score'] = (data['Spread'] - spread_mean) / spread_std

# --- THE NEW STUFF: GENERATING POSITIONS & PNL ---

# 3. Create Vectorized Trading Signals
# Rule 1: Z < -2.0 -> Buy the Spread (1)
# Rule 2: Z > 2.0 -> Short the Spread (-1)
# Rule 3: Z is between -0.5 and 0.5 -> Close Position (0) (Taking profit near the mean)
conditions = [
    data['Z_Score'] < -2.0,
    data['Z_Score'] > 2.0,
    abs(data['Z_Score']) < 0.5 
]
choices = [1, -1, 0]

# np.select applies the rules. If no rule is met, it returns NaN.
data['Signal'] = np.select(conditions, choices, default=np.nan)

# Forward-fill (ffill) the signals. This means if we enter a 1, we hold 1 until we hit a 0.
data['Position'] = data['Signal'].ffill().fillna(0)

# SHIFT BY 1 to avoid Look-Ahead Bias!
data['Position'] = data['Position'].shift(1)

# 4. Calculate PnL in Raw Dollars
# We calculate how much the spread price changed from yesterday
data['Spread_Change'] = data['Spread'].diff()

# Our daily profit is our position (1, -1, or 0) multiplied by the spread change
data['Daily_PnL'] = data['Position'] * data['Spread_Change']

# Cumulative sum of our daily profits
data['Cumulative_PnL'] = data['Daily_PnL'].cumsum()

# 5. Plot the Equity Curve
plt.figure(figsize=(10,6))
plt.plot(data.index, data['Cumulative_PnL'], label='Strategy PnL (Raw Dollars)', color='green', linewidth=2)
plt.title(f"Pairs Trading PnL: {tickers[0]} vs {tickers[1]} (Non-Cointegrated Test)")
plt.ylabel("Cumulative Profit ($ per 1 share spread)")
plt.legend()
plt.grid(True)
plt.show()

print(f"Total Profit/Loss from Spread Trading: ${data['Cumulative_PnL'].iloc[-1]:.2f} per share unit.")