import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import itertools

# 1. Define our basket of bank stocks
tickers = ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS']
print(f"Downloading data for {len(tickers)} bank stocks...")
data = yf.download(tickers, period="5y")

# Isolate Close prices and drop missing data
data = data['Close'].copy()
data.dropna(inplace=True)

# 2. Generate every possible pair combination
# combinations() takes our list of 6 stocks and pairs them up 2 by 2
pairs = list(itertools.combinations(tickers, 2))
print(f"Testing {len(pairs)} possible combinations for cointegration...\n")

# This empty list will store our scorecards
results = []

# 3. Loop through the pairs, run the math, and grade them
for pair in pairs:
    stock1 = pair[0]
    stock2 = pair[1]
    
    y = data[stock1]
    x = data[stock2]
    x_with_constant = sm.add_constant(x)
    
    # Calculate Hedge Ratio
    model = sm.OLS(y, x_with_constant).fit()
    hedge_ratio = model.params.iloc[1]
    
    # Calculate Spread
    spread = y - (hedge_ratio * x)
    
    # Run the ADF Cointegration Test
    p_value = adfuller(spread)[1]
    
    # Save the grade to our scorecard
    results.append({
        'Pair': f"{stock1} vs {stock2}",
        'P_Value': p_value,
        'Hedge_Ratio': hedge_ratio
    })

# 4. Rank the results to find the holy grail
results_df = pd.DataFrame(results)
# Sort from lowest P-Value (best) to highest (worst)
results_df = results_df.sort_values(by='P_Value')

print("--- Top 5 Best Pairs to Trade ---")
print(results_df.head(5).to_string(index=False))

# Evaluate our #1 prospect
best_pair = results_df.iloc[0]
if best_pair['P_Value'] < 0.05:
    print(f"\nSUCCESS: {best_pair['Pair']} is highly cointegrated! Let's trade it.")
else:
    print("\nWARNING: No strong cointegration found in this basket. Do not trade these right now.")