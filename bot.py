import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# 1. Connect to Alpaca
load_dotenv()
api = tradeapi.REST(
    os.getenv('APCA_API_KEY_ID'), 
    os.getenv('APCA_API_SECRET_KEY'), 
    os.getenv('APCA_API_BASE_URL'), 
    api_version='v2'
)

# --- NEW STUFF: PLACING A TRADE ---

symbol = 'GS'
qty = 1

print(f"Submitting market order to buy {qty} share(s) of {symbol}...")

try:
    # 2. Submit the order
    order = api.submit_order(
        symbol=symbol,
        qty=qty,
        side='buy',
        type='market',
        time_in_force='gtc' # Stays active until filled
    )
    
    print(f"\nSUCCESS! Order ID: {order.id}")
    print(f"Order Status: {order.status}")
    
    # 3. Check our current positions
    print("\n--- Current Portfolio ---")
    positions = api.list_positions()
    
    if not positions:
        print("No open positions yet (the order might still be processing, or the market is closed).")
    else:
        for position in positions:
            print(f"Holding {position.qty} shares of {position.symbol} (Avg Price: ${position.avg_entry_price})")

except Exception as e:
    print(f"Order Failed. Error: {e}")