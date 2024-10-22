import pandas as pd
import datetime as dt
import os
from logger import init_logger
from trco.analysis import get_active_cnt

logger = init_logger("./logs/generate_price_series.log")

def main():
    start = dt.datetime(2022,9,26)
    end = dt.datetime(2024,7,3)
    date_range = pd.bdate_range(start, end, freq = "D")

    data = []
    for x in date_range:
        print(x)
        fname = f"./data/future_chain_time_series/USA_Future_Settlement_{x:%Y%m%d}.parquet"
        if not os.path.isfile(fname):
            logger.info(f"Date {x} missing")
            continue

        dft = pd.read_parquet(fname, engine='pyarrow')
        dft.insert(loc=0, column='eod', value=x)
        dfc = get_active_cnt(dft)
        if dfc.empty:
            logger.warning(f"Warning: for date {x} missing open interest and volume column")
            continue
        data.append(dfc)

    dff = pd.concat(data, axis = 0)
    #dff = dff.loc[dff['symbol'] != dff['symbol'].shift(1)]
    output = "./data/continuous_price_series.csv"
    logger.info(f"Writing output to {output}")
    dff.to_csv(f"./data/continuous_price_series.csv", sep = ",", index = False)

if __name__ == "__main__":
    main()
