import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from config import PALETTE, ORDERED_MATURITIES
from computations import standardize, moving_average, moving_volatility
from cache import get_yields

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import yfinance as yf #SOLO PER TESTARE, DA LEVARE!!!
'''
time_period = "1y"

df1 = yf.download("AAPL", period=time_period)["Close"]
df2 = yf.download("GOOGL", period=time_period)["Close"]
df = pd.concat([df1, df2], axis=1)
df.columns = ["AAPL", "GOOGL"]'''
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
INTRADAY_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "1h", "90m"]

def default_settings(fig: plt.Figure, ax: plt.Axes, palette: tuple = PALETTE) -> None:
    # Set the background color
    fig.patch.set_facecolor(palette[0][0])
    ax.set_facecolor(palette[0][0])

    # Set the title and labels
    ax.set_title("Title",color=palette[6][0], fontsize=14)

    # Set the grid
    ax.grid(axis = 'y', color=palette[7][0], linestyle="-", linewidth=0.5, alpha=0.6)

    # Set the tick parameters
    ax.tick_params(axis='x', colors=palette[7][0])
    ax.tick_params(axis='y', colors=palette[7][0])

    #set spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    #set spines color
    ax.spines['left'].set_color(palette[7][0])
    ax.spines['bottom'].set_color(palette[7][0])

    #set line width
    for line in ax.lines:
        line.set_linewidth(1.75)
    
    #set legend background color
    ax.legend(facecolor=palette[7][0])

def graph_compare(ax: plt.Axes, fig: plt.Figure, df1: pd.DataFrame, df2: pd.DataFrame = None, standardized: bool = False) -> None:
        if df2 is None:
            df2 = df1.iloc[:, 1]
            df2.index = df1.index
            df1 = df1.iloc[:, 0]
        
        if standardized:
            df1 = standardize(df1)
            df2 = standardize(df2)

        ax.plot(df1.index, df1.values, color=PALETTE[6][0], linewidth=1.5, label=f"{df1.columns[0]}")
        ax.plot(df2.index, df2.values, color=PALETTE[5][0], linewidth=1.5, label=f"{df2.columns[0]}")
    
        default_settings(fig, ax)

        ax.set_title(f"Comparison between {df1.columns[0]} and {df2.columns[0]}")
    
        ax.legend()
    
def set_dates(ax: plt.Axes, time_horizon: str, last_date: str = None) -> None:
    if time_horizon == "1d":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif time_horizon == "1mo":
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d"))
    elif time_horizon == "3mo":
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    elif time_horizon == "6mo":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    elif time_horizon == "1y":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    
    if last_date is not None:
        last_date_num = mdates.datestr2num(last_date)
        ticks = ax.get_xticks()
        new_ticks = np.sort(np.append(ticks, last_date_num))
        ax.set_xticks(new_ticks)

def widget_term_structure(country_1: str, country_2: str = None, spread: bool = False) -> tuple[plt.Figure, pd.DataFrame]:
    countries = [c for c in [country_1, country_2] if c is not None]
    
    fig, ax = plt.subplots()
    
    curves_data = {country: get_yields(country) for country in countries}
    all_labels = [m for m in ORDERED_MATURITIES if any(m in curve for curve in curves_data.values())]

    label_to_x = {label: i for i, label in enumerate(all_labels)}

    all_curves = []

    ds_to_download = pd.DataFrame(index=all_labels)

    for idx, country in enumerate(countries):
        treasury_dict = curves_data[country]
        
        x_labels = [m for m in ORDERED_MATURITIES if m in treasury_dict]
        x_values = [label_to_x[m] for m in x_labels]
        current_yields = [treasury_dict[m] for m in x_labels]

        all_curves.append({
            "country": country,
            "labels": x_labels,
            "x": x_values,
            "y": current_yields
        })

        ds_to_download[country] = pd.Series(current_yields, index=x_labels)
    
        ax.plot(x_values, current_yields, label=country, color=PALETTE[-idx + 6][0], linewidth=1.5, marker="o")
        
    max_by_maturity = {}

    for curve in all_curves:
        for label, x, y in zip(curve["labels"], curve["x"], curve["y"]):
            if label not in max_by_maturity or y > max_by_maturity[label]["y"]:
                max_by_maturity[label] = {"x": x, "y": y}
    
    for item in max_by_maturity.values():
        ax.plot([item["x"], item["x"]], [0, item["y"]], color=PALETTE[7][0], linewidth=0.5, alpha=0.6, linestyle="--")
        
    default_settings(fig, ax)
        
    ax.spines['bottom'].set_position(('data', 0))
    ax.set_title("Term Structure of Treasury Yields")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=2))
    
    ax.grid(axis='y', color=PALETTE[7][0], linestyle="--", linewidth=0.5, alpha=0.6)

    ax.set_xticks(np.arange(len(all_labels)))
    ax.set_xticklabels(all_labels)

    ax.legend()

    if spread and country_2 is not None:
        curve_1 = dict(zip(all_curves[0]["labels"], all_curves[0]["y"]))
        curve_2 = dict(zip(all_curves[1]["labels"], all_curves[1]["y"]))

        common_labels = [m for m in ORDERED_MATURITIES if m in curve_1 and m in curve_2]

        x = [label_to_x[m] for m in common_labels]
        y1 = np.array([curve_1[m] for m in common_labels])
        y2 = np.array([curve_2[m] for m in common_labels])

        ax.fill_between(
            x,
            y1,
            y2,
            where=(y2 > y1),
            color= PALETTE[3][0], #green
            alpha=0.3
        )

        ax.fill_between(
        x,
        y1,
        y2,
        where=(y2 < y1),
        color= PALETTE[4][0], #red
        alpha=0.3
        )

    return fig,  ds_to_download

def pie_hole(portfolio: dict) -> None: # creare dizionario con ticker e pesi come variabile della class portfolio
    fig, ax = plt.subplots()
    weights_unsorted = list(portfolio.values())
    tickers_unsorted = list(portfolio.keys())
    idxs = []
    tickers = []

    weights = sorted(weights_unsorted)
    for idx, w in enumerate(weights):
        unsorted_value_idx = weights_unsorted.index(w)
        idxs.append((idx, unsorted_value_idx))
        weights_unsorted[unsorted_value_idx] = "done"
    
    for x in idxs:
        idx = x[1]
        tickers.append(tickers_unsorted[idx])

    
    colors = plt.cm.Blues(np.linspace(0.1, 0.8, len(weights)))

    ax.pie(weights,
        labels=tickers,
        counterclock=True,
        wedgeprops=dict(width=0.4),
        colors=colors,
        textprops={"color": PALETTE[6][0]}
    )

    return fig

def widget_line_chart(ticker: str,
                      start_date: str = None,
                      end_date: str = None,
                      period: str = None,
                      interval: str = "1d",
                      show_ma: bool = False,
                      ma_window: int = 20,
                      show_vol: bool = False,
                      chart_width: int = 600
    ) -> tuple[plt.Figure, pd.DataFrame]:
    if period == None:
        true_end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1) if end_date is not None else None

        datas = yf.download(ticker, start=start_date, end=true_end_date, interval=interval)[["Close", "Volume"]]
    else:
        datas = yf.download(ticker, period=period, interval=interval)[["Close", "Volume"]]
    data = datas["Close"]

    if isinstance(data, pd.DataFrame):
        data = data.squeeze()

    ds_to_download = pd.DataFrame({ticker: data})
    
    fig, ax = plt.subplots()

    x = np.arange(len(data))
    
    ax.plot(x, data.values, color=PALETTE[6][0], label=ticker)

    max_ticks = max(2, min(6, chart_width // 110))
    ticks = np.linspace(0, len(data) - 1, min(max_ticks, len(data)), dtype=int)
    
    ticks = np.unique(ticks)

    if interval in INTRADAY_INTERVALS:
        labels = [data.index[i].strftime("%m-%d\n%H:%M") for i in ticks]
    else:
        labels = [data.index[i].strftime("%y-%m-%d") for i in ticks]

    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.set_xticklabels(labels, rotation=0, ha="center", fontsize=8)

    ax.set_facecolor(PALETTE[1][0])
    fig.patch.set_facecolor(PALETTE[1][0])

    for spine in ax.spines.values():
        spine.set_color(PALETTE[7][0])
    
    ax.tick_params(axis="both", colors=PALETTE[7][0])

    ax.grid(visible=True, axis="y", alpha=0.5)

    if show_ma == True:
        ma = moving_average(data, window=ma_window)
        ax.plot(x, ma.values, color=PALETTE[5][0], label=f"MA {ma_window}")
        
        ds_to_download["MA"] = ma
    
    if show_vol == True:
        vol = datas["Volume"]

        if isinstance(vol, pd.DataFrame):
            vol = vol.squeeze()

        ax1 = ax.twinx()

        ax1.tick_params(axis="y", colors=PALETTE[7][0])
        ax1.spines["right"].set_color(PALETTE[7][0])
        ax1.spines["top"].set_visible(False)
        ax1.spines["left"].set_visible(False)
        ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))

        
        ax1.bar(x, vol.values, color=PALETTE[8][0], label="Volume", linewidth=0, alpha=0.25)

        ax.set_zorder(2)
        ax1.set_zorder(1)

        ax.patch.set_visible(False)

        ds_to_download["Volume"]=vol

    fig.tight_layout(pad=2)
    fig.subplots_adjust(bottom=0.18)    

    return fig, ds_to_download

def widget_candlestick_chart(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    period: str = "1d",
    interval: str = "5m",
    chart_width: int = 600
    ) -> tuple[plt.Figure, pd.DataFrame]:

    if period == None:
        true_end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1) if end_date is not None else None

        data = yf.download(ticker, start=start_date, end=true_end_date, interval=interval)[["Open", "Close", "High", "Low"]]
    else:
        data = yf.download(ticker, period=period, interval=interval)[["Open", "Close", "High", "Low"]]
    
    if isinstance(data.columns, pd.MultiIndex):
        data = data.droplevel(1, axis=1)

    days = data.index
    days_close = data["Close"]
    days_open = data["Open"]
    days_high = data["High"]
    days_low = data["Low"]

    up_days = days_close >= days_open
    down_days = days_close < days_open

    oc_width = 0.8 # width of the central part (Delta Open - Close)
    hl_width = 0.1 # width of the little bars (High and Low)

    ds_to_download = data.copy()

    fig, ax = plt.subplots()
    
    x = np.arange(len(data))
    # Up days
    ax.bar(x[up_days], days_close[up_days] - days_open[up_days], width=oc_width, bottom=days_open[up_days], color = PALETTE[3][0], alpha = 0.9)
    ax.bar(x[up_days], days_high[up_days] - days_close[up_days], width=hl_width, bottom=days_close[up_days], color = PALETTE[3][0])
    ax.bar(x[up_days], days_open[up_days] - days_low[up_days], width=hl_width, bottom=days_low[up_days], color = PALETTE[3][0])

    # Down days
    ax.bar(x[down_days], days_open[down_days] - days_close[down_days], width=oc_width, bottom=days_close[down_days], color = PALETTE[4][0], alpha = 0.9)
    ax.bar(x[down_days], days_high[down_days] - days_open[down_days], width=hl_width, bottom=days_open[down_days], color = PALETTE[4][0])
    ax.bar(x[down_days], days_close[down_days] - days_low[down_days], width=hl_width, bottom=days_low[down_days], color = PALETTE[4][0])

    max_ticks = max(2, min(6, chart_width // 110))
    ticks = np.linspace(0, len(data) - 1, min(max_ticks, len(data)), dtype=int)
    
    ticks = np.unique(ticks)

    if interval in INTRADAY_INTERVALS:
        labels = [days[i].strftime("%m-%d\n%H:%M") for i in ticks]
    else:
        labels = [days[i].strftime("%y-%m-%d") for i in ticks]

    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    ax.set_facecolor(PALETTE[1][0])
    fig.patch.set_facecolor(PALETTE[1][0])

    for spine in ax.spines.values():
        spine.set_color(PALETTE[7][0])
    
    ax.tick_params(axis="both", colors=PALETTE[7][0])

    ax.grid(visible=True, color=PALETTE[7][0], alpha = 0.5)
    
    fig.tight_layout(pad=2)
    fig.subplots_adjust(bottom=0.18)

    return fig, ds_to_download


if __name__ == "__main__":
    fig = widget_candlestick_chart("AAPL", period="1d", interval="5m") # USE "USA" FOR MORE ACCURATE DATA, USE "US" TO COMPARE WITH OTHER NATIONS
    plt.show()
