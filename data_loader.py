import yfinance as yf
import pandas as pd
import numpy as np
import requests
from io import StringIO

from datetime import date, timedelta
from fredapi import Fred

from config import DEFAULT_DATE_FORMAT, DATA_SOURCES, COUNTRY_SLUGS, WGB_BASE_URL, WGB_COUNTRIES, COUNTRY_SYMBOLS
from log import log_error
from cache import get_infos, get_yields

fmt = DEFAULT_DATE_FORMAT

def current_price(ticker: str):
    t = yf.Ticker(ticker)

    # tries retrieving live price
    try:
        price = t.fast_info.get("lastPrice")
        if price is not None:
            return price
    except Exception:
        pass
    
    # fallback: last recent close
    data = t.history(period="5d")
    if not data.empty:
        return data["Close"].iloc[-1].item()
    
    return log_error("No value found")

def open_price(ticker: str, date: str = "today"):
    t = yf.Ticker(ticker)
    
    if date == "today":
        price = t.fast_info.get("open")
    else:
        data = yf.download(ticker, start=date)
        price = data["Open"].iloc[0] if not data.empty else None

    return price

def get_currency(ticker: str):
    t = yf.Ticker(ticker)

    try:
        currency = t.fast_info.get("currency")
        if currency is not None:
            return currency
    except Exception:
        pass

    try:
        data = yf.download(ticker, period = "1d", progress = False)
        return data.attrs.get("currency")
    except Exception:
        pass

    try:
        currency = t.info.get("currency")
        if currency is not None:
            return currency
    except Exception:
        pass

    return None
        
def convert_to_currency(df: pd.DataFrame, ticker: str = None, target_currency: str = "EUR"):
    if ticker == None:
        ticker = df.columns[0]

    t = yf.Ticker(ticker)
    currency = t.info.get("currency")

    if currency == None:
        log_error(f"Currency of {ticker} not found")
        return None
    
    if currency != target_currency:
        fx_str = f"{target_currency}{currency}=X"

        start = df.index[0]
        end = df.index[-1]

        end_plus_one = end + timedelta(days=1)
        end_plus_one = end_plus_one.strftime(fmt) # this is because download excludes the end date

        exchange = yf.download(fx_str, start=start, end = end_plus_one)["Close"].iloc[:, 0]

        exchange = exchange.reindex(df.index).ffill()
 
        return df.div(exchange, axis=0)
    return df

def download_treasury_history() -> dict:
    fred = Fred(api_key=get_infos("fred_api_key"))
    list_dgs = ["DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS5", "DGS10", "DGS30"]
    yields = {}

    for dgs in list_dgs:
        yields[dgs] = fred.get_series(dgs)

    return {
        "date": date.today(),
        "data": yields
    }

def download_wgb_yields(country:str) -> dict:
    yields = {}

    # AAA EUROZONE INTEREST RATES
    if country == "AAA Eurozone":

        wanted = {
            "3M": "SR_3M",
            "6M": "SR_6M",
            "9M": "SR_9M",
            "1Y": "SR_1Y",
            "2Y": "SR_2Y",
            "3Y": "SR_3Y",
            "4Y": "SR_4Y",
            "5Y": "SR_5Y",
            "10Y": "SR_10Y",
            "30Y": "SR_30Y"
        }

        df = pd.read_csv(DATA_SOURCES[country])
        mask_AAA = df[df.iloc[:,5] == "G_N_A"]
        mask_SR = mask_AAA[mask_AAA.iloc[:,7].str.startswith("SR_")]

        for idx, mat in enumerate(wanted.values()):
            today_spot = mask_SR[mask_SR.iloc[:,7] == mat].iloc[:,9].iloc[0]
            yields[list(wanted.keys())[idx]] = today_spot

    # All EUROZONE INTEREST RATES
    elif country == "All Eurozone":
        wanted = {
            "3M": "SR_3M",
            "6M": "SR_6M",
            "9M": "SR_9M",
            "1Y": "SR_1Y",
            "2Y": "SR_2Y",
            "3Y": "SR_3Y",
            "4Y": "SR_4Y",
            "5Y": "SR_5Y",
            "10Y": "SR_10Y",
            "30Y": "SR_30Y"
        }

        df = pd.read_csv(DATA_SOURCES[country])
        mask_All = df[df.iloc[:,5] == "G_N_C"]
        mask_SR = mask_All[mask_All.iloc[:,7].str.startswith("SR_")]

        for idx, mat in enumerate(wanted.values()):
            today_spot = mask_SR[mask_SR.iloc[:,7] == mat].iloc[:,9].iloc[0]
            yields[list(wanted.keys())[idx]] = today_spot

    # WGB COUNTRIES
    else:
        slug = COUNTRY_SLUGS[country]
        url = f"{WGB_BASE_URL}/{slug}/"

        payload = {
            "GLOBALVAR": {
                "JS_VARIABLE": "jsGlobalVars",
                "FUNCTION": "Country",
                "DOMESTIC": True,
                "ENDPOINT": "https://www.worldgovernmentbonds.com/wp-json/country/v1/historical",
                "DATE_RIF": "2099-12-31",
                "OBJ": None,
                "COUNTRY1": {
                    "SYMBOL": COUNTRY_SYMBOLS[country],
                    "PAESE": country,
                    "PAESE_UPPERCASE": country.upper(),
                    "URL_PAGE": slug,
                },
                "COUNTRY2": None,
                "OBJ1": None,
                "OBJ2": None,
            }
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.worldgovernmentbonds.com",
            "Referer": url,
            "Content-Type": "application/json"
        }

        r = requests.post(
            "https://www.worldgovernmentbonds.com/wp-json/country/v1/main",
            json=payload,
            headers=headers
        )

        r.raise_for_status()
        result = r.json()

        if not result.get("success"):
            raise ValueError(f"WGB request failed for {country}: {result}")

        html_table = result["mainTable"]

        df = pd.read_html(StringIO(html_table))[0]
        
        maturity_col = ("Residual Maturity", "Residual Maturity")
        yield_col = ("Annualized Yield", "Last")

        wanted = {
            "1 month": "1M",
            "3 months": "3M",
            "6 months": "6M",
            "9 months": "9M",
            "1 year": "1Y",
            "2 years": "2Y",
            "3 years": "3Y",
            "4 years": "4Y",
            "5 years": "5Y",
            "10 years": "10Y",
            "15 years": "15Y",
            "20 years": "20Y",
            "25 years": "25Y",
            "30 years": "30Y",
            "50 years": "50Y",
        }
        
        for _, row in df.iterrows():
            maturity_raw = str(row[maturity_col]).strip().lower()
            yield_raw = str(row[yield_col]).strip()

            if maturity_raw in wanted:
                label = wanted[maturity_raw]

                value = float(yield_raw.replace("%", "").strip())
                yields[label] = value
            
    return{
        "date": date.today(),
        "data": yields
    }

def download_yields(country: str) -> dict:
    if country == "USA":
        dictionary = download_treasury_history()
        cache_date = dictionary["date"]
        fred_data = dictionary["data"]

        fred_to_maturity = {
            "DGS1MO": "1M",
            "DGS3MO": "3M",
            "DGS6MO": "6M",
            "DGS1": "1Y",
            "DGS2": "2Y",
            "DGS5": "5Y",
            "DGS10": "10Y",
            "DGS30": "30Y",
        }

        yields = {}

        for fred_code, maturity in fred_to_maturity.items():
            series = fred_data[fred_code]
            yields[maturity] = series.dropna().iloc[-1]
        
        return {"date": cache_date, "data": yields}
    
    if country in WGB_COUNTRIES:
        return download_wgb_yields(country)

    raise log_error(f"Country {country} is not supported")

def get_first_available(*values):
    for value in values:
        if value is not None:
            return value
    return None

def _get_first_available_key(data: dict | str, keys: list, history: bool = False):
    for key in keys:
        if history:
            series = yf.download(data, auto_adjust=False, progress=False)[key] # CONTROLLARE SE FUNZIONA

            if isinstance(series, pd.DataFrame):
                value = series.iloc[:, 0]

            value = series.iloc[-1] if not series.empty else None
        else:
            value = data.get(key)

        if value is not None:
            return value

    return None

def get_infos(ticker: str, keys: list, fast: bool = False, history: bool = False):
    t = yf.Ticker(ticker)

    if history:
        return _get_first_available_key(ticker, keys, history = True)
    if fast:
        info = dict(t.fast_info)
    else:
        info = t.info

    return _get_first_available_key(info, keys)
        
def get_ath(ticker:str):
    history = yf.download(ticker, period="max", progress=False, auto_adjust=False)["High"]

    if isinstance(history, pd.DataFrame):
        history = history.iloc[:, 0]

    return max(history)

def daily_vol(ticker:str, annualized: bool = False):
    data = yf.download(ticker, period="1d", interval="1m", auto_adjust= False, progress= False)
    t = data["Close"]

    if isinstance(data, pd.DataFrame):
        t = data.iloc[:, 0]

    t = t.dropna()

    returns = t.pct_change().dropna()
    vol = returns.std()

    if annualized == True:
        return vol * np.sqrt(252 * 6.5 * 60)
    
    return vol

def get_max_drawdown(ticker: str, pct_fmt: bool = True):
    history = yf.download(ticker, period="max", progress=False, auto_adjust=False)["Close"]

    if isinstance(history, pd.DataFrame):
        history = history.iloc[:, 0]

    history = history.dropna()

    prices = history.to_numpy(dtype=np.float64)

    running_max = np.maximum.accumulate(prices, axis=0)
    drawdown = prices / running_max - 1
    
    if pct_fmt == True:
        drawdown = drawdown * 100

    return np.min(drawdown, axis=0)

if __name__ == "__main__":
    download_wgb_yields("Germany")
    