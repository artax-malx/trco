import pandas as pd
import numpy as np
from itertools import product
import logging

def calc_pnl(current_price, entry_price, contract_size, slippage):
    return (current_price - entry_price)*contract_size

def simulate_trading(df, X, Y, Z):
    pnl = 0
    position = None  
    entry_price = 0
    contract_size = 10

    slippage_bps = 0 
    
    trades = []

    for i in range(max(X, Y), len(df)):
        current_price = df.loc[i, 'settlement_price']
        current_day = df.loc[i, "eod"]
        
        trade_pnl = calc_pnl(current_price, entry_price, contract_size, slippage_bps)

        # Check Stop-Loss
        if position == 'buy' and (trade_pnl < -1 * Z):
            pnl += trade_pnl 
            position = None 
            trades.append((current_day, trade_pnl)) 
        elif position == 'sell' and (-1*trade_pnl < -1 * Z):
            trade_pnl = -1*trade_pnl
            pnl += trade_pnl 
            position = None
            trades.append((current_day, trade_pnl)) 

        # Check Signals
        if current_price >= df.loc[i - X: i-1, 'settlement_price'].max():
            # If position is already a sell, don't do anything with signal,
            # since position is already taken
            if position == 'buy':
                trade_pnl = calc_pnl(current_price, entry_price, contract_size, slippage_bps)
                pnl += trade_pnl 
                trades.append((current_day, trade_pnl)) 
                position = 'sell'
                entry_price = current_price
            elif position is None:
                position = 'sell'
                entry_price = current_price

        elif current_price <= df.loc[i - Y:i - 1, 'settlement_price'].min():
            # If position is already a buy, don't do anything with signal,
            # since position is already taken
            if position == 'sell':
                trade_pnl = -1*calc_pnl(current_price, entry_price, contract_size, slippage_bps)
                pnl += trade_pnl 
                trades.append((current_day, trade_pnl)) 
                position = 'buy'
                entry_price = current_price
            elif position is None:
                position = 'buy'
                entry_price = current_price

    return pnl, trades

def main():

    fname = f"./data/continuous_price_series.csv"
    df = pd.read_csv(fname, sep = ",")
    
    df['eod'] = pd.to_datetime(df['eod'], format="%Y-%m-%d")
    df = df.sort_values('eod').reset_index(drop=True)
    
    in_sample_period = 60
    out_sample_period = 30 
    
    X_range = range(3, 50)  
    Y_range = range(3, 50)  
    Z_range = np.linspace(10, 500, 30) 
    
    # Walk-forward analysis
    results = []
    all_trades = []

    endpoint = len(df) - in_sample_period - out_sample_period
    for start in range(0, endpoint, out_sample_period):

        in_sample_start = df.iloc[start, 0]
        in_sample_end = df.iloc[start + in_sample_period, 0]
        out_sample_end = df.iloc[start + in_sample_period + out_sample_period, 0]

        in_sample_df = df.iloc[start:start + in_sample_period]
        out_sample_df = df.iloc[start + in_sample_period:start + in_sample_period + out_sample_period]

        print(f"In-sample period: {in_sample_start} - {in_sample_end} | Out-sample period: {in_sample_end} - {out_sample_end}")
    
        best_params = None
        best_pnl = -np.inf
    
        print(">>> Started in sample testing")
        for X, Y, Z in product(X_range, Y_range, Z_range):
            current_pnl, _ = simulate_trading(in_sample_df.reset_index(drop=True), X, Y, Z)
            
            if current_pnl > best_pnl:
                best_pnl = current_pnl
                best_params = (X, Y, Z)
    
        X_opt, Y_opt, Z_opt = best_params
        print(f">>> Started out of sample testing with params {X_opt}, {Y_opt}, {Z_opt}")
        out_sample_pnl, out_trades = simulate_trading(out_sample_df.reset_index(drop=True), X_opt, Y_opt, Z_opt)
    
        results.append({
            'start_date': out_sample_df['eod'].iloc[0],
            'end_date': out_sample_df['eod'].iloc[-1],
            'X': X_opt,
            'Y': Y_opt,
            'Z': Z_opt,
            'in_sample_pnl': best_pnl,
            'out_sample_pnl': out_sample_pnl
        })
        all_trades += out_trades
    
    results_df = pd.DataFrame(results)
    trades_df = pd.DataFrame(all_trades)
    trades_df.columns = ['eod', 'pnl']

    return results_df, trades_df

if __name__ == "__main__":
    res,trds = main()
    res.to_csv("./data/countertrend_system_res.csv", sep= ",", index = False)
    trds.to_csv("./data/countertrend_system_trades.csv", sep= ",", index = False)
