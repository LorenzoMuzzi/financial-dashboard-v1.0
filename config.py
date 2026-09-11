import pandas as pd

APP_TITLE = "Financial Dashboard"
WINDOW_SIZE = "1200x800"
WINDOW_MODE = "zoomed"

API_KEY = "" # just to remember, delete it in the end

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL"]
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_END_DATE = None  # None = oggi

DEFAULT_DATE_FORMAT = "%Y-%m-%d"

PALETTE = (("#020A17", "Background"), #0
        ("#0F172A", "Panel"), #1
        ("#38BDF8", "Accent"), #2
        ("#22C55E", "Positive"), #3
        ("#EF4444", "Negative"), #4
        ("#F59E0B", "Benchmark"), #5
        ("#E2E8F0", "Text"), #6
        ("#94A3B8", "Subtext"), #7
        ("#A216E3", "Secondary"), #8
        ("#111C33", "Lighter Panel")) #9

DEFAULT_INTERVAL = "1d"

TIMEZONES = {
    "Italy": "Europe/Rome",
    "UK": "Europe/London",
    "US East": "America/New_York",
    "US Central": "America/Chicago",
    "US West": "America/Los_Angeles",
    "Japan": "Asia/Tokyo",
    "China": "Asia/Shanghai",
    "Hong Kong": "Asia/Hong_Kong",
    "Singapore": "Asia/Singapore",
    "Australia": "Australia/Sydney",
    "UTC": "UTC"
}

CHART_STYLE = {
    "figure_size": (8, 4),
    "line_width": 1.5,
    "grid": False,
}

YAHOO_SETTINGS = {
    "auto_adjust": True,
    "progress": False,
}

MAX_PANELS = 6

AVAILABLE_WIDGETS = {
    "line_chart": "Line Chart",
    "candlestick_chart": "Candlestick Chart",
    "term_structure": "Term Structure",
    "list_widget": "List Widget"
}

# INTEREST RATES
DATA_SOURCES = {
    "AAA Eurozone": "https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A+G_N_C.SV_C_YM.?lastNObservations=1&format=csvdata",
    "All Eurozone": "https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A+G_N_C.SV_C_YM.?lastNObservations=1&format=csvdata"
}

COUNTRY_SLUGS = {
    # North America
    "US": "united-states",
    "Canada": "canada",
    "Mexico": "mexico",

    # South America
    "Brazil": "brazil",
    "Chile": "chile",
    "Peru": "peru",
    "Colombia": "colombia",

    # Europe, main countries
    "UK": "united-kingdom",
    "Germany": "germany",
    "France": "france",
    "Italy": "italy",
    "Spain": "spain",
    "Portugal": "portugal",
    "Netherlands": "netherlands",
    "Belgium": "belgium",
    "Austria": "austria",
    "Switzerland": "switzerland",
    "Ireland": "ireland",
    "Greece": "greece",

    # Northern Europe
    "Sweden": "sweden",
    "Norway": "norway",
    "Denmark": "denmark",
    "Finland": "finland",

    # Europe, large / relevant non-core countries
    "Poland": "poland",
    "Czech Republic": "czech-republic",
    "Hungary": "hungary",
    "Romania": "romania",
    "Russia": "russia",
    "Turkey": "turkey",

    # Asia
    "Japan": "japan",
    "China": "china",
    "India": "india",
    "South Korea": "south-korea",
    "Singapore": "singapore",
    "Malaysia": "malaysia",
    "Indonesia": "indonesia",
    "Thailand": "thailand",
    "Vietnam": "vietnam",

    # Oceania
    "Australia": "australia",
    "New Zealand": "new-zealand",

    # Africa / MENA
    "South Africa": "south-africa",
    "Morocco": "morocco",
    "Egypt": "egypt",
}

WGB_COUNTRIES = list(COUNTRY_SLUGS.keys())

WGB_BASE_URL = "https://www.worldgovernmentbonds.com/country"

COUNTRY_SYMBOLS = {
    # North America
    'US': '6',
    'Canada': '21',
    'Mexico': '14',

    # South America
    'Brazil': '7',
    'Chile': '34',
    'Peru': '67',
    'Colombia': '35',

    # Europe, main countries
    'UK': '5',
    'Germany':'2',
    'France': '3',
    'Italy': '1',
    'Spain': '4',
    'Portugal': '16',
    'Netherlands': '26',
    'Belgium': '31',
    'Austria': '27',
    'Switzerland': '24',
    'Ireland': '40',
    'Greece': '15',

    # Northern Europe
    'Sweden': '19',
    'Norway': '18',
    'Denmark': '37',
    'Finland': '17',

    # Europe, large / relevant non-core countries
    'Poland': '20',
    'Czech Republic': '50',
    'Hungary': '57',
    'Romania': '51',
    'Russia': '10',
    'Turkey': '13',

    # Asia
    'Japan': '11',
    'China': '9',
    'India': '8',
    'South Korea': '29',
    'Singapore': '52',
    'Malaysia': '46',
    'Indonesia': '39',
    'Thailand': '53',
    'Vietnam': '58',

    # Oceania
    'Australia': '22',
    'New Zealand': '47',

    # Africa / MENA
    'South Africa': '28',
    'Morocco': '63',
    'Egypt': '30'
}

ORDERED_MATURITIES = ["1M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "7Y", "10Y", "15Y", "20Y", "25Y", "30Y"]

LIST_COLUMNS = {
    # Identity
    "ticker": {"label": "Ticker", "width": 70, "source": "manual", "yf_keys": []},
    "name": {"label": "Name", "width": 80, "source": "info", "yf_keys": ["longName", "shortName", "displayName"]},
    "exchange": {"label": "Exchange", "width": 80, "source": "info", "yf_keys": ["exchange", "fullExchangeName"]},
    "currency": {"label": "Currency", "width": 40, "source": "fast_info", "yf_keys": ["currency"]},
    "country": {"label": "Country", "width": 80, "source": "info", "yf_keys": ["country"]},
    "sector": {"label": "Sector", "width": 80, "source": "info", "yf_keys": ["sector"]},
    "industry": {"label": "Industry", "width": 80, "source": "info", "yf_keys": ["industry"]},
    "asset_type": {"label": "Asset Type", "width": 60, "source": "info", "yf_keys": ["quoteType"]},

    # Price
    "price": {"label": "Price", "width": 60, "source": "fast_info", "yf_keys": ["last_price", "lastPrice", "regularMarketPrice", "currentPrice"]},
    "open": {"label": "Open", "width": 60, "source": "fast_info", "yf_keys": ["open", "regularMarketOpen"]},
    "prev_close": {"label": "Previous Close", "width": 60, "source": "fast_info", "yf_keys": ["previous_close", "previousClose", "regularMarketPreviousClose"]},
    "day_high": {"label": "Day High", "width": 60, "source": "fast_info", "yf_keys": ["day_high", "regularMarketDayHigh"]}, # NA
    "day_low": {"label": "Day Low", "width": 60, "source": "fast_info", "yf_keys": ["day_low", "regularMarketDayLow"]}, # NA
    "bid": {"label": "Bid", "width": 60, "source": "info", "yf_keys": ["bid"]},
    "ask": {"label": "Ask", "width": 60, "source": "info", "yf_keys": ["ask"]},
    "mid_price": {"label": "Mid Price", "width": 60, "source": "calculated", "yf_keys": []},

    # Change
    "chg": {"label": "Change", "width": 60, "source": "info", "yf_keys": ["regularMarketChange"]},
    "pct_chg": {"label": "% Chg", "width": 60, "source": "info", "yf_keys": ["regularMarketChangePercent"]},
    "chg_from_open": {"label": "Change From Open", "width": 60, "source": "calculated", "yf_keys": []},
    "pct_chg_from_open": {"label": "% Chg From Open", "width": 60, "source": "calculated", "yf_keys": []},
    "range": {"label": "Range", "width": 60, "source": "calculated", "yf_keys": []},
    "pct_range": {"label": "% Range", "width": 60, "source": "calculated", "yf_keys": []},

    # Volume
    "volume": {"label": "Volume", "width": 80, "source": "fast_info", "yf_keys": ["last_volume", "lastVolume", "regularMarketVolume", "volume"]},
    "avg_volume": {"label": "Average Volume", "width": 80, "source": "fast_info", "yf_keys": ["average_volume", "averageVolume", "averageDailyVolume10Day", "averageVolume10days"]},
    "rel_volume": {"label": "Relative Volume", "width": 80, "source": "calculated", "yf_keys": []},
    "turnover": {"label": "Turnover", "width": 80, "source": "calculated", "yf_keys": []},

    # Performance
    "perf_1d": {"label": "1D %", "width": 60, "source": "history", "yf_keys": []},
    "perf_5d": {"label": "5D %", "width": 60, "source": "history", "yf_keys": []},
    "perf_1mo": {"label": "1M %", "width": 60, "source": "history", "yf_keys": []},
    "perf_3mo": {"label": "3M %", "width": 60, "source": "history", "yf_keys": []},
    "perf_6mo": {"label": "6M %", "width": 60, "source": "history", "yf_keys": []},
    "perf_ytd": {"label": "YTD %", "width": 60, "source": "history", "yf_keys": []},
    "perf_1y": {"label": "1Y %", "width": 60, "source": "history", "yf_keys": []},
    "perf_5y": {"label": "5Y %", "width": 60, "source": "history", "yf_keys": []},

    # High / Low
    "high_52w": {"label": "52W High", "width": 60, "source": "info", "yf_keys": ["fiftyTwoWeekHigh"]},
    "low_52w": {"label": "52W Low", "width": 60, "source": "info", "yf_keys": ["fiftyTwoWeekLow"]},
    "pct_from_52w_high": {"label": "% From 52W High", "width": 60, "source": "calculated", "yf_keys": ["fiftyTwoWeekHighChangePercent"]},
    "pct_from_52w_low": {"label": "% From 52W Low", "width": 60, "source": "calculated", "yf_keys": ["fiftyTwoWeekLowChangePercent"]},
    "ath": {"label": "All Time High", "width": 60, "source": "history", "yf_keys": []},
    "pct_from_ath": {"label": "% From ATH", "width": 60, "source": "calculated", "yf_keys": []},

    # Risk
    "daily_volatility": {"label": "Daily Volatility", "width": 60, "source": "history", "yf_keys": []},
    "annualized_volatility": {"label": "Annualized Volatility", "width": 60, "source": "history", "yf_keys": []},
    "beta": {"label": "Beta", "width": 60, "source": "info", "yf_keys": ["beta"]},
    "max_drawdown": {"label": "Max Drawdown", "width": 60, "source": "history", "yf_keys": []},
    "atr": {"label": "ATR", "width": 60, "source": "history", "yf_keys": []},
}

PERFORMANCE_PERIODS = {
    "1d": pd.DateOffset(days=1),
    "5d": pd.DateOffset(days=5),
    "1mo": pd.DateOffset(months=1),
    "3mo": pd.DateOffset(months=3),
    "6mo": pd.DateOffset(months=6),
    "1y": pd.DateOffset(years=1),
    "5y": pd.DateOffset(years=5),
}