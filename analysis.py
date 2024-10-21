import pandas as pd
import datetime as dt
import os

fmap = "./cocoa_assignment_data/map_qid_to_future_contract.csv"
dfm = pd.read_csv(fmap, sep = ",")
MAP_DICT = dfm.set_index("qid").to_dict()

def get_active_cnt(df):
    df['expiration_date'] = df['qid'].map(MAP_DICT['expiration_date'])
    df['symbol'] = df['qid'].map(MAP_DICT['symbol'])

    df['expiration_date'] = pd.to_datetime(df['expiration_date'], format="%d/%m/%Y")
    df['rem_maturity'] = df['expiration_date'] - df['eod']

    if not df['open_interest'].isnull().all():
        idrow = df['open_interest'].idxmax()
    elif not df['rem_maturity'].isnull().all():
        idrow = df['volume'].idxmax()
        #idrow = df['rem_maturity'].idxmin()
    else:
        return pd.DataFrame([]) 

    df = df.loc[[idrow],:].copy()

    return df

if __name__ == "__main__":
    start = dt.datetime(2022,9,26)
    end = dt.datetime(2024,7,3)
    date_range = pd.date_range(start, end, freq = "D")

    data = []
    for x in date_range:
        print(x)
        fname = f"./cocoa_assignment_data/future_chain_time_series/USA_Future_Settlement_{x:%Y%m%d}.parquet"
        if not os.path.isfile(fname):
            print(">>> Date {x} missing")
            continue
        dft = pd.read_parquet(fname, engine='pyarrow')
        dft.insert(loc=0, column='eod', value=x)
        dfc = get_active_cnt(dft)
        if dfc.empty:
            raise Exception(f"ERROR: for date {x} missing open interest and maturity column")
        data.append(dfc)

    dff = pd.concat(data, axis = 0)
    dff = dff.loc[dff['symbol'] != dff['symbol'].shift(1)]
