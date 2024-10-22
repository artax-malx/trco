import pandas as pd
import datetime as dt
import logging
import matplotlib.pyplot as plt
import numpy as np

fmap = "./data/map_qid_to_future_contract.csv"
dfm = pd.read_csv(fmap, sep = ",")
MAP_DICT = dfm.set_index("qid").to_dict()

def get_active_cnt(df):
    df['expiration_date'] = df['qid'].map(MAP_DICT['expiration_date'])
    df['symbol'] = df['qid'].map(MAP_DICT['symbol'])

    df['expiration_date'] = pd.to_datetime(df['expiration_date'], format="%d/%m/%Y")
    df['rem_maturity'] = df['expiration_date'] - df['eod']

    if not df['open_interest'].isnull().all():
        idrow = df['open_interest'].idxmax()
    elif not df['volume'].isnull().all():
        logging.warning(f"Open Interest column empty for data: {df['eod'].iloc[0]}")
        idrow = df['volume'].idxmax()
    else:
        return pd.DataFrame([]) 

    df = df.loc[[idrow],:].copy()

    return df

def plot(df, x_col, y_col):
    df.set_index(x_col).plot(y = y_col, figsize=(10,6))
    plt.title("Cocoa Active Contract")
    plt.xlabel("Date")
    plt.ylabel(y_col)
    plt.savefig(f'data/active_contract_{y_col}_timeseries.png', dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    df = pd.read_csv("./data/continuous_price_series.csv", sep = ",")
    df['log_returns'] = np.log(df['settlement_price']).diff(periods=1)
    plot(df, "eod", "settlement_price")
    plot(df, "eod", "log_returns")

    trades = pd.read_csv("./data/countertrend_system_trades.csv", sep = ",")
    trades['equity'] = trades['pnl'].cumsum()
    trades.set_index("eod").plot(y = "equity", figsize=(10,6))
    plt.title("Equity Curve")
    plt.xlabel("Date")
    plt.savefig(f'data/equity_curve.png', dpi=300, bbox_inches="tight")
