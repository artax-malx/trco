import pandas as pd
import datetime as dt
import logging

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

