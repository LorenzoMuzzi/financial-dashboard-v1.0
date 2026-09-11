import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf #SOLO PER TESTARE, DA LEVARE!!!

from config import PALETTE, PERFORMANCE_PERIODS
from log import log_error

def moving_average(df: pd.Series | pd.DataFrame, window: int = 30) -> pd.Series:
    ma = df.rolling(window=window).mean()
    return ma

def moving_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    returns = df.pct_change()
    return returns.rolling(window).std() * np.sqrt(252)

def standardize(df: pd.DataFrame | pd.Series) -> pd.DataFrame:
    if isinstance(df, pd.Series):
        df = df.to_frame()
    
    df_pct = df.pct_change()
    df_pct = df_pct.fillna(0)
    data = {}

    for col in df_pct.columns:
        list_std = [100]
        first = True

        for var in df_pct.loc[:, col]:
            if first:
                first = False
                continue
            cng = list_std[-1] * (1 + var)
            list_std.append(cng)
        
        data[col] = list_std

    df_std = pd.DataFrame(data, index=df.index)
    return df_std

def performance(ticker: str, time_period: str = "1d", pct_fmt: bool = False) -> float:
    df = yf.download(ticker, period = time_period, auto_adjust=False, progress=False,)["Close"]
    change = (df.iloc[-1] / df.iloc[0] - 1).iloc[0]

    if df.empty:
        log_error(f"No data found for {ticker}, period={time_period}")
        return None

    if pct_fmt == True:
        change = change * 100

    return change

def _get_start_period(period: str, anchor_date: pd.Timestamp):
    anchor_date = pd.Timestamp(anchor_date).normalize()

    if period == "ytd":
        return pd.Timestamp(year= anchor_date.year, month = 1, day = 1)
    
    return anchor_date - PERFORMANCE_PERIODS.get(period)

def period_performance(ticker: str, period: str = "1d", pct_fmt: bool = False):
    today = pd.Timestamp.today().normalize()

    if period == "ytd":
        rough_start = pd.Timestamp(year=today.year, month= 1, day = 1) - pd.Timedelta(days= 10)
    else:
        rough_start = today - PERFORMANCE_PERIODS.get(period) - pd.Timedelta(days= 10)

    df = yf.download(ticker, start=rough_start, progress=False, auto_adjust=False)

    if df.empty:
        return None

    close = df["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = close.dropna()

    last_date = close.index[-1]
    start_period = _get_start_period(period, last_date)

    start_close = close[close.index <= start_period].iloc[-1]
    last_close = close.iloc[-1]

    change = last_close / start_close - 1

    if pct_fmt:
        change *= 100

    return float(change)

def get_mid_price(ticker:str):
    t = yf.Ticker(ticker)
    bid = t.info.get("bid")
    ask = t.info.get("ask")

    return (bid + ask)/2
    


if __name__ == "__main__":
    df1 = yf.download("AAPL", period="1y")["Close"]
    df2 = yf.download("GOOGL", period="1y")["Close"]