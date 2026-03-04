import os
import yfinance as yf
import statsmodels.api as sm
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# 1. Connect to Broker
load_dotenv()
api = tradeapi.REST(
    os.getenv('APCA_API_KEY_ID'), 
    os.getenv('APCA_API_SECRET_KEY'), 
    os.getenv('APCA_API_BASE_URL'), 
    api_version='v2'
)

# 2. Fetch Latest Market Data (Using 1 Year to establish the baseline)
tickers = ['GS', 'MS']
print(f"Analyzing Live Spread for {tickers[0]} and {tickers[1]}...\n")

data = yf.download(tickers, period="1y")['Close'].dropna()

# 3. Calculate Live Z-Score
y = data['GS']
x = data['MS']
x_with_constant = sm.add_constant(x)
model = sm.OLS(y, x_with_constant).fit()
hedge_ratio = model.params.iloc[1]

spread = y - (hedge_ratio * x)
z_score = (spread - spread.mean()) / spread.std()

# Grab the absolute latest Z-score from today
current_z = z_score.iloc[-1]
print(f"--- CURRENT MARKET CONDITIONS ---")
print(f"Hedge Ratio: {hedge_ratio:.2f}")
print(f"Live Z-Score: {current_z:.2f}\n")

# 4. The Decision Engine
print("--- TRADING ACTION ---")
try:
    if current_z < -2.0:
        print("Signal: BUY THE SPREAD (Rubber band stretched down)")
        # Buy GS, Short MS
        api.submit_order(symbol='GS', qty=10, side='buy', type='market', time_in_force='gtc')
        api.submit_order(symbol='MS', qty=10, side='sell', type='market', time_in_force='gtc')
        print("Orders Submitted: Bought 10 GS, Shorted 10 MS.")

    elif current_z > 2.0:
        print("Signal: SHORT THE SPREAD (Rubber band stretched up)")
        # Short GS, Buy MS
        api.submit_order(symbol='GS', qty=10, side='sell', type='market', time_in_force='gtc')
        api.submit_order(symbol='MS', qty=10, side='buy', type='market', time_in_force='gtc')
        print("Orders Submitted: Shorted 10 GS, Bought 10 MS.")

    elif abs(current_z) < 0.5:
        print("Signal: TAKE PROFIT (Rubber band returned to normal)")
        # Close all positions
        api.close_all_positions()
        print("Orders Submitted: Closed all open positions.")

    else:
        print("Signal: HOLD / DO NOTHING (Spread is in the normal range)")

except Exception as e:
    print(f"Execution Error: {e}")