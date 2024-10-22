import pandas as pd
import numpy as np
from itertools import product

fname = f"./data/continuous_price_series.csv"
df = pd.read_csv(fname, sep = ",")

df['eod'] = pd.to_datetime(df['eod'], format="%Y-%m-%d")
df = df.sort_values('eod').reset_index(drop=True)

in_sample_period = 60
out_sample_period = 30 
contract_size = 10  

X_range = range(3, 50)  
Y_range = range(3, 50)  
Z_range = np.linspace(10, 500, 30) 

def simulate_trading(df, X, Y, Z):
    pnl = 0
    position = None  
    entry_price = 0
    
    trades = []

    for i in range(max(X, Y), len(df)):
        current_price = df.loc[i, 'settlement_price']
        current_day = df.loc[i, "eod"]
        
        # If we have an active position, check for stop-loss
        if position == 'buy' and ((current_price - entry_price)*contract_size < -1 * Z):
            trade_pnl = (current_price - entry_price)*contract_size
            pnl += trade_pnl 
            position = None  # Exit position
            trades.append([current_day, trade_pnl,"buy"]) 
        
        elif position == 'sell' and (-1*(current_price - entry_price)*contract_size < -1*Z):
            trade_pnl = -1*(current_price - entry_price)*contract_size
            pnl += trade_pnl 
            position = None  # Exit position
            trades.append([current_day, trade_pnl,"sell"]) 

        # Check trading signals only if no position is active, or switch positions when a signal appears
        # Buy signal: if the current price is the highest in the last X days
        if current_price >= df.loc[i - X: i-1, 'settlement_price'].max():
            if position == 'sell':
                # Close the short position and switch to a long position
                trade_pnl =  (entry_price - current_price) * contract_size
                pnl += trade_pnl 
                trades.append([current_day, trade_pnl,"buy"]) 

                position = 'buy'
                entry_price = current_price
            elif position is None:
                # Open a new buy position if no position exists
                position = 'buy'
                entry_price = current_price

        # Sell signal: if the current price is the lowest in the last Y days
        elif current_price <= df.loc[i - Y:i - 1, 'settlement_price'].min():
            if position == 'buy':
                # Close the long position and switch to a short position
                trade_pnl = (current_price - entry_price) * contract_size
                pnl += trade_pnl 
                trades.append([current_day, trade_pnl,"sell"]) 

                position = 'sell'
                entry_price = current_price
            elif position is None:
                # Open a new sell position if no position exists
                position = 'sell'
                entry_price = current_price

    return pnl

# Walk-forward analysis
results = []

# Iterate through the entire date range for walk-forward analysis
for start in range(0, len(df) - in_sample_period - out_sample_period, out_sample_period):
    print(start, start + in_sample_period, start + in_sample_period, start + in_sample_period + out_sample_period)
    in_sample_df = df.iloc[start:start + in_sample_period]
    out_sample_df = df.iloc[start + in_sample_period:start + in_sample_period + out_sample_period]

    # Optimize parameters using the in-sample period
    best_params = None
    best_pnl = -np.inf

    print(">>> Started inin  sample testing")
    # Try all combinations of X, Y, Z
    for X, Y, Z in product(X_range, Y_range, Z_range):
        # Simulate trading with the current parameters on the in-sample period
        current_pnl = simulate_trading(in_sample_df.reset_index(drop=True), X, Y, Z)
        
        # Check if the current combination is better
        if current_pnl > best_pnl:
            best_pnl = current_pnl
            best_params = (X, Y, Z)

    # Use the best parameters for out-of-sample trading
    X_opt, Y_opt, Z_opt = best_params
    print(f">>> Started out of sample testing: {X_opt}, {Y_opt}, {Z_opt}")
    out_sample_pnl = simulate_trading(out_sample_df.reset_index(drop=True), X_opt, Y_opt, Z_opt)

    # Store the result for each walk-forward period
    results.append({
        'start_date': out_sample_df['eod'].iloc[0],
        'end_date': out_sample_df['eod'].iloc[-1],
        'X': X_opt,
        'Y': Y_opt,
        'Z': Z_opt,
        'in_sample_pnl': best_pnl,
        'out_sample_pnl': out_sample_pnl
    })

# Create a DataFrame to view the results
results_df = pd.DataFrame(results)
print(results_df)

