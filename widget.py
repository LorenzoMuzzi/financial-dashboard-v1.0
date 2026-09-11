import tkinter as tk
from tkinter import StringVar, ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from pathlib import Path

from config import PALETTE, TIMEZONES, COUNTRY_SLUGS, LIST_COLUMNS
from graph import INTRADAY_INTERVALS, widget_line_chart, widget_term_structure, widget_candlestick_chart
from log import log_error
from data_loader import get_first_available, current_price, open_price, get_currency, get_infos, get_ath, daily_vol, get_max_drawdown
from computations import performance, get_mid_price, period_performance

PERIODS = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max"
    ]
INTERVALS = [
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "1h",
    "90m",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo"
]

# HELPER FUNCTIONS
def only_int(value):
    return value == "" or value.isdigit()

def build_scrollable_controls(parent, bg = PALETTE[1][0], height = 45):
        controls_container = tk.Frame(parent, bg=bg)
        controls_container.pack(side="top", fill="x")

        canvas = tk.Canvas(
            controls_container,
            bg = bg,
            highlightthickness=0,
            height=height
        )
        canvas.pack(side="top", fill="x", expand=True)

        scrollbar = tk.Scrollbar(
            controls_container,
            orient="horizontal",
            command=canvas.xview
        )
        scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=scrollbar.set)

        controls = tk.Frame(canvas, bg=bg)
        canvas.create_window((0,0), window=controls, anchor="nw")

        controls.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        return controls

def load_icon(path, size=(15, 15)):
    icon = Image.open(path)
    icon = icon.resize(size)
    return ImageTk.PhotoImage(icon)

def ask_export_path():
    return filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[
            ("Excel file", "*.xlsx"),
            ("CSV file", "*.csv")
        ]
    )

# DEFAULT CLASS =======================================================================================================================
class DashboardWidget(tk.Frame):
    widget_type = None

    def __init__(self, parent, state=None):
        super().__init__(parent, bg=PALETTE[1][0])
        self.state = state or {}
        self.state_fields = {}

    def register_state_field(self, name, getter):
        self.state_fields[name] = getter

    def get_state(self):
        state = {"type": self.widget_type}

        for name, getter in self.state_fields.items():
            state[name] = getter()

        return state

# LINE WIDGET ==========================================================================================================================================================
class LineWidget(DashboardWidget):
    widget_type = "line_chart"

    def __init__(self, parent, state= None, autorun = False):
        super().__init__(parent, state=state)

        self.download_icon = load_icon("icons/download_icon.png")

        self._build_controls()
        self._build_chart_area()

        if autorun:
            self.after(100, self.update_chart)

        self.df = None

    def _build_controls(self):
        controls = build_scrollable_controls(parent=self, bg=PALETTE[1][0], height=25)

        # TICKER
        ticker_label = tk.Label(controls, text="Ticker:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        ticker_label.pack(side="left", padx=(5, 3))

        self.ticker_entry = tk.Entry(controls, width=7)
        self.ticker_entry.insert(0, self.state.get("ticker", "AAPL"))
        self.ticker_entry.pack(side="left", padx=(0, 5))

        # PERIOD
        period_label = tk.Label(controls, text="Period:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        period_label.pack(side="left", padx=(5, 3))

        periods = ["-"] + PERIODS

        self.period_entry = ttk.Combobox(
            controls,
            values=periods,
            width=5,
            state="readonly"
        )

        self.period_entry.set(self.state.get("period", "6mo"))
        self.period_entry.pack(side="left", padx=(0, 5))

        # START DATE
        sdate_label = tk.Label(controls, text="Start date:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        sdate_label.pack(side="left", padx=(5, 3))

        self.sdate_entry = DateEntry(
            controls,
            width=10,
            date_pattern="yyyy-mm-dd",
            background= PALETTE[0][0],
            foreground= PALETTE[6][0],
            borderwidth=2
        )

        self.sdate_entry.pack(side="left", padx=(0, 5))

        # END DATE
        edate_label = tk.Label(controls, text="End date:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        edate_label.pack(side="left", padx=(5, 3))

        self.edate_entry = DateEntry(
            controls,
            width=10,
            date_pattern="yyyy-mm-dd",
            background= PALETTE[0][0],
            foreground= PALETTE[6][0],
            borderwidth=2
        )

        self.edate_entry.pack(side="left", padx=(0, 5))

        # INTERVAL
        interval_label = tk.Label(controls, text="Interval:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        interval_label.pack(side="left", padx=5)

        intervals = INTERVALS

        self.interval_entry = ttk.Combobox(
            controls,
            values=intervals,
            width=5,
            state="readonly"
        )

        self.interval_entry.set(self.state.get("interval", "1d"))
        self.interval_entry.pack(side="left", padx=(0, 5))

        # MOVING AVERAGE
        self.show_moving_avg = tk.BooleanVar(value=self.state.get("show_ma", False))

        moving_avg_check = tk.Checkbutton(
            controls,
            text="- Moving Average",
            variable=self.show_moving_avg,
            bg=PALETTE[1][0],
            fg=PALETTE[6][0],
            selectcolor=PALETTE[1][0],
            activebackground=PALETTE[1][0],
            activeforeground=PALETTE[6][0]
        )

        moving_avg_check.pack(side="left", padx=(10, 3))

        vcmd = self.register(only_int)

        self.ma_window_entry = tk.Entry(
            controls,
            width=3,
            validate="key",
            validatecommand=(vcmd, "%P")
        )

        self.ma_window_entry.insert(0, "20")
        self.ma_window_entry.pack(side="left", padx=(0, 5))

        # VOLUME
        self.show_vol = tk.BooleanVar(value=self.state.get("show_vol", False))

        vol_check = tk.Checkbutton(
            controls,
            text="- Volume",
            variable=self.show_vol,
            bg=PALETTE[1][0],
            fg=PALETTE[6][0],
            selectcolor=PALETTE[1][0],
            activebackground=PALETTE[1][0],
            activeforeground=PALETTE[6][0]
        )

        vol_check.pack(side="left", padx=(0, 5))
        
        # TIME-ZONE
        time_label = tk.Label(controls, text="Timezone:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        time_label.pack(side="left", padx=(5, 3))

        timezones = ["Default"] + list(TIMEZONES.keys())

        self.tz_entry = ttk.Combobox(
            controls,
            values=timezones,
            width=7,
            state="readonly"
        )

        self.tz_entry.set(self.state.get("timezone", "Default"))
        self.tz_entry.pack(side="left", padx=(0, 5))

        # PLOT
        btn = tk.Button(
            controls,
            text="Plot",
            command=self.update_chart
        )
        btn.pack(side="left", padx=5)

        self.register_state_field("ticker", self.ticker_entry.get)
        self.register_state_field("period", self.period_entry.get)
        self.register_state_field("start_date", self.sdate_entry.get)
        self.register_state_field("end_date", self.edate_entry.get)
        self.register_state_field("interval", self.interval_entry.get)
        self.register_state_field("show_ma", self.show_moving_avg.get)
        self.register_state_field("ma_window", self.ma_window_entry.get)
        self.register_state_field("show_vol", self.show_vol.get)
        self.register_state_field("timezone", self.tz_entry.get)

        # EXPORT
        export = tk.Button(
            controls,
            image=self.download_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command= self._export
            )
        export.pack(side="left", padx=3)

    def _build_chart_area(self):
        self.chart_area = tk.Frame(self, bg=PALETTE[1][0])
        self.chart_area.pack(side="bottom", fill="both", expand=True)

    def update_chart(self):
        ticker = self.ticker_entry.get()
        period = self.period_entry.get()
        start_date = self.sdate_entry.get()
        end_date = self.edate_entry.get()
        interval = self.interval_entry.get()
        show_moving_avg = self.show_moving_avg.get()
        ma_window = int(self.ma_window_entry.get() or 20)
        show_vol = self.show_vol.get()
        chart_width = self.chart_area.winfo_width()
        if chart_width <= 1:
            chart_width = 600
        timezone = self.tz_entry.get()

        if period == "-":
            period = None

        for child in self.chart_area.winfo_children():
            child.destroy()

        fig, self.df = widget_line_chart(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            period=period,
            interval=interval,
            show_ma=show_moving_avg,
            ma_window=ma_window,
            show_vol=show_vol,
            chart_width=chart_width
        )

        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        if interval in INTRADAY_INTERVALS:
            if timezone == "Default":
                self.df.index = self.df.index.tz_localize(None)
            else:
                self.df.index = (self.df.index.tz_convert(TIMEZONES[timezone]).tz_localize(None))
        else:
            self.df.index = self.df.index.date

    def _export(self):
        if self.df is None:
                return

        file_path = ask_export_path()

        if not file_path:
            return

        ext = Path(file_path).suffix.lower()

        if ext == ".xlsx":
            self.df.to_excel(file_path, index=True)
        elif ext == ".csv":
            self.df.to_csv(file_path, index=True)
# TERM STRUCTURE WIDGET =================================================================================================================================================
class TermWidget(DashboardWidget):
    widget_type = "term_structure"

    def __init__(self, parent, state= None, autorun = False):
        super().__init__(parent, state=state)

        self.download_icon = load_icon("icons/download_icon.png")

        countries_list = ["USA"] + list(COUNTRY_SLUGS.keys())
        countries_list.sort()
        self.COUNTRIES = [""] + countries_list
        

        self._build_controls()
        self._build_chart_area()

        if autorun:
            self.after(100, self.update_chart)

    def _build_controls(self):
        controls = build_scrollable_controls(
                parent=self,
                bg=PALETTE[1][0],
                height=25
            )

        # COUNTRY ENTRY
        country_label = tk.Label(controls, text="Country:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        country_label.pack(side="left", padx=(5, 3))

        self.country_entry = ttk.Combobox(
            controls,
            values=self.COUNTRIES,
            width=11,
            state="readonly"
        )

        self.country_entry.set(self.state.get("country", "USA"))
        self.country_entry.pack(side="left", padx=(0, 5))

        # BENCHMARK ENTRY
        benchmark_label = tk.Label(controls, text="Benchmark:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        benchmark_label.pack(side="left", padx=(5, 3))

        self.benchmark_entry = ttk.Combobox(
            controls,
            values=self.COUNTRIES,
            width=11,
            state="readonly"
        )

        self.benchmark_entry.set(self.state.get("benchmark", ""))
        self.benchmark_entry.pack(side="left", padx=(0, 5))

        # SPREAD
        self.spread = tk.BooleanVar(value=self.state.get("spread", False))

        spread_check = tk.Checkbutton(
            controls,
            text="- Spread",
            variable=self.spread,
            bg=PALETTE[1][0],
            fg=PALETTE[6][0],
            selectcolor=PALETTE[1][0],
            activebackground=PALETTE[1][0],
            activeforeground=PALETTE[6][0]
        )

        spread_check.pack(side="left", padx=(0, 5))

        # PLOT
        btn = tk.Button(
            controls,
            text="Plot",
            command=self.update_chart
        )
        btn.pack(side="left", padx=5)

        self.register_state_field("country", self.country_entry.get)
        self.register_state_field("benchmark", self.benchmark_entry.get)
        self.register_state_field("spread", self.spread.get)

        # EXPORT
        export = tk.Button(
            controls,
            image=self.download_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command= self._export
            )
        export.pack(side="left", padx=3)
    
    def _build_chart_area(self):
        self.chart_area = tk.Frame(self, bg=PALETTE[1][0])
        self.chart_area.pack(side="bottom", fill="both", expand=True)
    
    def update_chart(self):
        country = self.country_entry.get()
        benchmark = self.benchmark_entry.get()
        spread = self.spread.get()

        if benchmark == "":
            benchmark = None
            spread = False

        for child in self.chart_area.winfo_children():
            child.destroy()

        fig, self.df = widget_term_structure(
            country_1= country,
            country_2= benchmark,
            spread=spread
        )

        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _export(self):
        if self.df is None:
                return

        file_path = ask_export_path()

        if not file_path:
            return

        ext = Path(file_path).suffix.lower()

        if ext == ".xlsx":
            self.df.to_excel(file_path, index=True)
        elif ext == ".csv":
            self.df.to_csv(file_path, index=True)
        else:
            log_error("Formato non supportato")
# CANDLESTICK WIDGET ==========================================================================================================================================================
class CandleStickWidget(DashboardWidget):
    widget_type = "candlestick_chart"

    def __init__(self, parent, state= None, autorun = False):
        super().__init__(parent, state=state)

        self.download_icon = load_icon("icons/download_icon.png")

        self._build_controls()
        self._build_chart_area()

        if autorun:
            self.after(100, self.update_chart)

        self.df = None
    
    def _build_controls(self):
        controls = build_scrollable_controls(
            parent=self,
            bg=PALETTE[1][0],
            height=25
        )

        # TICKER
        ticker_label = tk.Label(controls, text="Ticker:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        ticker_label.pack(side="left", padx=(5, 3))

        self.ticker_entry = tk.Entry(controls, width=7)
        self.ticker_entry.insert(0, self.state.get("ticker", "AAPL"))
        self.ticker_entry.pack(side="left", padx=(0, 5))

        # PERIOD
        period_label = tk.Label(controls, text="Period:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        period_label.pack(side="left", padx=(5, 3))

        periods = ["-"] + PERIODS

        self.period_entry = ttk.Combobox(
            controls,
            values=periods,
            width=5,
            state="readonly"
        )

        self.period_entry.set(self.state.get("period", "1d"))
        self.period_entry.pack(side="left", padx=(0, 5))

        # START DATE
        sdate_label = tk.Label(controls, text="Start date:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        sdate_label.pack(side="left", padx=(5, 3))

        self.sdate_entry = DateEntry(
            controls,
            width=10,
            date_pattern="yyyy-mm-dd",
            background= PALETTE[0][0],
            foreground= PALETTE[6][0],
            borderwidth=2
        )

        self.sdate_entry.pack(side="left", padx=(0, 5))

        # END DATE
        edate_label = tk.Label(controls, text="End date:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        edate_label.pack(side="left", padx=(5, 3))

        self.edate_entry = DateEntry(
            controls,
            width=10,
            date_pattern="yyyy-mm-dd",
            background= PALETTE[0][0],
            foreground= PALETTE[6][0],
            borderwidth=2
        )

        self.edate_entry.pack(side="left", padx=(0, 5))

        # INTERVAL
        interval_label = tk.Label(controls, text="Interval:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        interval_label.pack(side="left", padx=5)

        intervals = INTERVALS

        self.interval_entry = ttk.Combobox(
            controls,
            values=intervals,
            width=5,
            state="readonly"
        )

        self.interval_entry.set(self.state.get("interval", "5m"))
        self.interval_entry.pack(side="left", padx=(0, 5))
        
        # TIME-ZONE
        time_label = tk.Label(controls, text="Timezone:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        time_label.pack(side="left", padx=(5, 3))

        timezones = ["Default"] + list(TIMEZONES.keys())

        self.tz_entry = ttk.Combobox(
            controls,
            values=timezones,
            width=7,
            state="readonly"
        )

        self.tz_entry.set(self.state.get("timezone", "Default"))
        self.tz_entry.pack(side="left", padx=(0, 5))

        # PLOT
        btn = tk.Button(
            controls,
            text="Plot",
            command=self.update_chart
        )
        btn.pack(side="left", padx=5)

        self.register_state_field("ticker", self.ticker_entry.get)
        self.register_state_field("period", self.period_entry.get)
        self.register_state_field("start_date", self.sdate_entry.get)
        self.register_state_field("end_date", self.edate_entry.get)
        self.register_state_field("interval", self.interval_entry.get)
        self.register_state_field("timezone", self.tz_entry.get)

        # EXPORT
        export = tk.Button(
            controls,
            image=self.download_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command= self._export
            )
        export.pack(side="left", padx=3)

    def _build_chart_area(self):
        self.chart_area = tk.Frame(self, bg=PALETTE[1][0])
        self.chart_area.pack(side="bottom", fill="both", expand=True)
    
    def update_chart(self):

        ticker = self.ticker_entry.get()
        period = self.period_entry.get()
        start_date = self.sdate_entry.get()
        end_date = self.edate_entry.get()
        interval = self.interval_entry.get()
        chart_width = self.chart_area.winfo_width()

        if chart_width <= 1:
            chart_width = 600
        
        timezone = self.tz_entry.get()

        if period == "-":
            period = None

        for child in self.chart_area.winfo_children():
            child.destroy()

        fig, self.df = widget_candlestick_chart(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            period=period,
            interval=interval,
            chart_width=chart_width
        )

        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        if interval in INTRADAY_INTERVALS:
            if timezone == "Default":
                self.df.index = self.df.index.tz_localize(None)
            else:
                self.df.index = (self.df.index.tz_convert(TIMEZONES[timezone]).tz_localize(None))
        else:
            self.df.index = self.df.index.date
    
    def _export(self):
        if self.df is None:
                return

        file_path = ask_export_path()

        if not file_path:
            return

        ext = Path(file_path).suffix.lower()

        if ext == ".xlsx":
            self.df.to_excel(file_path, index=True)
        elif ext == ".csv":
            self.df.to_csv(file_path, index=True)
# LIST WIDGET ==========================================================================================================================================================
class ListWidget(DashboardWidget):
    widget_type = "list_widget"

    def __init__(self, parent, state= None, autorun = False):
        super().__init__(parent, state=state)

        self.download_icon = load_icon("icons/download_icon.png")
        self.refresh_icon = load_icon("icons/refresh_icon.png")

        self.ticker_list = []
        self.selected_columns = ["ticker", "price", "pct_chg", "volume"]
        self.available_columns = LIST_COLUMNS

        self._build_controls()
        self._build_list_area()


        if autorun:
            self.after(100, self._refresh)

        self.df = None

    def _build_controls(self):
        controls = build_scrollable_controls(parent=self, bg=PALETTE[1][0], height=25)

        # TICKER
        ticker_label = tk.Label(controls, text="Ticker:", bg=PALETTE[1][0], fg=PALETTE[6][0])
        ticker_label.pack(side="left", padx=(5, 3))

        self.ticker_entry = tk.Entry(controls, width=7)
        self.ticker_entry.insert(0, self.state.get("ticker", "AAPL"))
        self.ticker_entry.pack(side="left", padx=(0, 5))

        # ADD
        btn = tk.Button(
            controls,
            text="Add",
            command=self.add_ticker
        )
        btn.pack(side="left", padx=5)

        # MANAGE COLUMNS
        btn = tk.Button(
            controls,
            text = "Columns",
            command = self._manage_columns_popup
        )
        btn.pack(side="left", padx=5)

        # REFRESH
        btn = tk.Button(
            controls,
            image=self.refresh_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command=self._refresh
        )
        btn.pack(side="left", padx=5)

        self.register_state_field("ticker_list", lambda: self.ticker_list.copy())
        self.register_state_field("selected_columns", lambda: self.selected_columns.copy())

        # EXPORT
        export = tk.Button(
            controls,
            image=self.download_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command= self._export
            )
        export.pack(side="left", padx=3)

    def _build_list_area(self):
        self.list_area = tk.Frame(self, bg=PALETTE[1][0])
        self.list_area.pack(side="bottom", fill="both", expand=True)

        # DEFINING THE STYLE ------------------------------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Default.Treeview", background = PALETTE[1][0], foreground = PALETTE[6][0], fieldbackground = PALETTE[1][0])
        style.configure("Default.Treeview.Heading", background = PALETTE[0][0], foreground = PALETTE[6][0], font = ("Arial", 9, "bold"))
        style.map("Default.Treeview", background = [("selected", PALETTE[2][0])], foreground = [("selected", PALETTE[6][0])])
        # -------------------------------------------------

        self.columns = tuple(self.selected_columns)

        self.tree = ttk.Treeview(self.list_area, columns = self.columns, show = "headings", style = "Default.Treeview")

        self.tree.bind("<Button-1>", self.clear_selection_if_empty)

        self._update_tree_columns()

        self.tree.tag_configure("oddrow", background = PALETTE[1][0], foreground = PALETTE[6][0])
        self.tree.tag_configure("evenrow", background = PALETTE[9][0], foreground = PALETTE[6][0])

        y_scroll = tk.Scrollbar(self.list_area, orient = "vertical", command = self.tree.yview)
        x_scroll = tk.Scrollbar(self.list_area, orient = "horizontal", command = self.tree.xview)

        self.tree.configure(yscrollcommand = y_scroll.set, xscrollcommand = x_scroll.set)
        self.tree.grid(row = 0, column = 0, sticky = "nsew")
        y_scroll.grid(row = 0, column = 1, sticky = "ns")
        x_scroll.grid(row = 1, column = 0, sticky = "ew")

        self.list_area.rowconfigure(0, weight = 1)
        self.list_area.columnconfigure(0, weight = 1)

    def add_ticker(self):
        ticker = self.ticker_entry.get().strip().upper()

        if ticker == "":
            return

        if ticker in self.ticker_list:
            return

        self.ticker_list.append(ticker)

        row_idx = len(self.ticker_list)
        if row_idx % 2 == 0:
            tag = "evenrow"
        else:
            tag = "oddrow"

        values = []

        for column in self.selected_columns:
            if column == "ticker":
                values.append(ticker)
            else:
                values.append("-") # paceholder value

        self.tree.insert("", "end", iid = ticker, values=values, tags = (tag,))

    def clear_selection_if_empty(self, event):
        row = self.tree.identify_row(event.y)

        if row == "":
            self.tree.selection_remove(self.tree.selection())

    def _manage_columns_popup(self):
        root = self.winfo_toplevel()

        popup = tk.Toplevel(root)
        popup.title("Columns management")
        popup.geometry("400x500")
        popup.transient(root)
        popup.grab_set()

        # POPUP GRID
        popup.rowconfigure(0, weight=2)  # Header
        popup.rowconfigure(1, weight=15)  # Body
        popup.rowconfigure(2, weight=3)  # Footer
        popup.columnconfigure(0, weight=1)

        # HEADER TEXT ------------------------------------------
        tk.Label(popup, text="Select the columns to display:").grid(row=0, column=0, padx=20)

        # BODY -------------------------------------------------
        body = tk.Frame(popup)
        body.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = "nsew")

        body.rowconfigure(0, weight = 1)
        body.columnconfigure(0, weight = 1)

        canvas = tk.Canvas(body, highlightthickness = 0)
        canvas.grid(row = 0, column = 0, sticky = "nsew")

        y_scroll = tk.Scrollbar(body, orient = "vertical", command = canvas.yview)
        y_scroll.grid(row = 0, column = 1, sticky = "ns")

        canvas.configure(yscrollcommand = y_scroll.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta)/ 120), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        checkbox_frame = tk.Frame(canvas)
        checkbox_frame.bind("<MouseWheel>", _on_mousewheel)

        window_id = canvas.create_window((0, 0), window = checkbox_frame, anchor = "nw")

        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def stretch_checkbox_frame(event):
            canvas.itemconfigure(window_id, width=event.width)

        checkbox_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", stretch_checkbox_frame)

        self.column_vars = {}

        for row_idx, (column_key, column_dict) in enumerate(self.available_columns.items()):
            column_name = column_dict["label"]
            if column_key == "ticker":
                var = tk.BooleanVar(value = True)
                state = "disabled"
            else:
                var = tk.BooleanVar(value = column_key in self.selected_columns)
                state = "normal"

            self.column_vars[column_key] = var

            check = tk.Checkbutton(
                checkbox_frame,
                text = column_name,
                variable = var,
                anchor = "w",
                state = state
            )
            check.grid(row = row_idx, column = 0, sticky = "w", pady = 2)

            check.bind("<MouseWheel>", _on_mousewheel)
        # FOOTER -----------------------------------------------
        footer = tk.Frame(popup)
        footer.grid(row = 2, column = 0, padx = 20, pady = 10, sticky = "ew")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)

        tk.Button(
        popup,
        text="Close",
        width=10,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=popup.destroy,
        ).grid(row=2, column=0, sticky="w", padx=20)

        tk.Button(
        popup,
        text="Save",
        width=10,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=lambda: self._save_columns(popup),
        ).grid(row=2, column=0, sticky="e", padx=20)

    def _save_columns(self, popup):
        selected = []

        for column_key, var in self.column_vars.items():
            if var.get():
                selected.append(column_key)

        if not selected:
            return

        self.selected_columns = selected
        self._update_tree_columns()

        popup.destroy()

    def _update_tree_columns(self):
        self.columns = tuple(self.selected_columns)
        self.tree.configure(columns = self.columns)

        for column_key in self.columns:
            column_name = self.available_columns[column_key]["label"]
            column_width = self.available_columns[column_key]["width"]

            self.tree.heading(column_key, text = column_name)
            self.tree.column(column_key, width = column_width, anchor = "center", stretch = False)

    def _refresh(self):
        if not self.ticker_list:
            return

        for t in self.ticker_list:
            values = []

            for col in self.selected_columns:
                if col == "ticker":
                    values.append(t)
                    continue

                source = self.available_columns[col]["source"]
                keys = self.available_columns[col]["yf_keys"]

                if source == "info":
                    value =  get_infos(t, keys)

                elif source == "fast_info":
                    value = get_infos(t, keys, fast = True)

                elif source == "history":
                    if keys:
                        value = get_infos(t, keys, history = True)
                    elif col.startswith("perf_"):
                        time_period = col.removeprefix("perf_")
                        value = period_performance(t, time_period, pct_fmt= True)
                    
                    elif col == "ath":
                        value = get_ath(t)

                    elif col == "daily_volatility":
                        value = daily_vol(t)
                    elif col == "annualized_volatility":
                        value = daily_vol(t, annualized= True)
                    elif col == "max_drawdown":
                        value = get_max_drawdown(t)
                    else:
                        value = "N/A" #CAPIRE COS'è ATR

                else: # if source == "calculated"
                    if keys:
                        value = get_infos(t, keys)

                    elif col == "mid_price":
                        value = get_mid_price(t)

                    elif col == "chg_from_open":
                        current = current_price(t)
                        open = open_price(t)

                        value = current - open

                    elif col == "pct_chg_from_open":
                        current = current_price(t)
                        open = open_price(t)

                        value = (current - open) / open * 100 if open != 0 else None

                    else:
                        value = None

                if value is None:
                    value = "N/A"

                values.append(value)

            self.tree.item(t, values=values)

    def _export(self):
            if self.df is None:
                    return
    
            file_path = ask_export_path()
    
            if not file_path:
                return
    
            ext = Path(file_path).suffix.lower()
    
            if ext == ".xlsx":
                self.df.to_excel(file_path, index=True)
            elif ext == ".csv":
                self.df.to_csv(file_path, index=True)

# LISTE PER dashboard.py ===============================================================================================================================================
WIDGET_CLASSES = {
            "line_chart": LineWidget,
            "term_structure": TermWidget,
            "candlestick_chart": CandleStickWidget,
            "list_widget": ListWidget
        }
WIDGET_LIST = list(WIDGET_CLASSES.keys())