import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# 1. Fetch Data for Two Competitors (Coke and Pepsi)
print("Downloading data for KO and PEP...")
tickers = ['KO', 'PEP']
data = yf.download(tickers, period="5y")

# Clean up the yfinance columns
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(0) # Drops the 'Price' level
    
data = data.dropna()

# 2. Find the Hedge Ratio (How much Coke equals one Pepsi?)
# We use Ordinary Least Squares (OLS) regression to find the ratio between the two
y = data['KO']
x = data['PEP']
x_with_constant = sm.add_constant(x)

# Run the regression
model = sm.OLS(y, x_with_constant).fit()
hedge_ratio = model.params['PEP']
print(f"Hedge Ratio: {hedge_ratio:.4f}")

# 3. Calculate the Spread
# Spread = Coke Price - (Hedge Ratio * Pepsi Price)
data['Spread'] = data['KO'] - (hedge_ratio * data['PEP'])

# 4. Run the Augmented Dickey-Fuller (ADF) Test
# This tests if the spread is "stationary" (meaning it reverts to a mean)
adf_result = adfuller(data['Spread'])
p_value = adf_result[1]

print("\n--- Cointegration Test Results ---")
print(f"ADF P-Value: {p_value:.4f}")

if p_value < 0.05:
    print("Result: STRONG COINTEGRATION! The spread is stationary. This is a tradable pair.")
else:
    print("Result: NO COINTEGRATION. Do not trade this pair.")

# 5. Plot the Spread
plt.figure(figsize=(10,4))
plt.plot(data.index, data['Spread'], label='Spread (KO - PEP)')
plt.axhline(data['Spread'].mean(), color='red', linestyle='--', label='Mean (Baseline)')
plt.title("Pairs Trading Spread: Coca-Cola vs. Pepsi")
plt.legend()
plt.grid(True)
plt.show()