import pandas as pd
from pathlib import Path
from datetime import date

CACHE_DIR = Path("cache")
CACHE_YIELDS = CACHE_DIR / "yield_curves.pkl"
CACHE_INFOS = CACHE_DIR / "infos.pkl"

def get_infos(field: str):
    CACHE_DIR.mkdir(exist_ok=True)

    if CACHE_INFOS.exists():
        cached_infos = pd.read_pickle(CACHE_INFOS)

        return cached_infos[field]
    
    return None

def save_infos(field: str, value) -> None:
    CACHE_DIR.mkdir(exist_ok=True)

    if CACHE_INFOS.exists():
        cached_infos = pd.read_pickle(CACHE_INFOS)
    else:
        cached_infos = {}

    cached_infos[field] = value
    pd.to_pickle(cached_infos, CACHE_INFOS)

def get_yields(country: str) -> dict:
    from data_loader import download_yields
    CACHE_DIR.mkdir(exist_ok=True)

    if CACHE_YIELDS.exists():
        try:
            cached = pd.read_pickle(CACHE_YIELDS)
        except Exception:
            cached = {}
    else:
        cached = {}
    
    country_cache = cached.get(country)

    if country_cache is not None:
        if country_cache.get("date") == date.today():
            return country_cache["data"]
    
    fresh_data = download_yields(country)
    cached[country] = fresh_data

    pd.to_pickle(cached, CACHE_YIELDS)

    return fresh_data["data"]
