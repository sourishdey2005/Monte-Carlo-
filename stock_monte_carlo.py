"""
╔══════════════════════════════════════════════════════════════════╗
║   MONTE CARLO STOCK SIMULATOR  —  Live Auto-Refresh Edition      ║
║   Free API: yfinance (Yahoo Finance) — No API key required       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta, date
import time
import warnings
import math
warnings.filterwarnings("ignore")

# ════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Monte Carlo Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.stApp { background: #080a10; color: #dde1f0; }
.main  { background: #080a10; }

h1,h2,h3,h4 { font-family: 'JetBrains Mono', monospace !important; }

.kpi { flex:1; min-width:140px; background:linear-gradient(145deg,#111320,#0c0e1a);
       border:1px solid #1e2236; border-radius:14px; padding:18px 16px; text-align:center; }
.klabel { font-size:10px; letter-spacing:2.5px; text-transform:uppercase;
               color:#4b5675; margin-bottom:8px; }
.kval   { font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:700; }
.kdelta { font-size:11px; margin-top:4px; opacity:.75; }
.pos { color:#22d3b0; } .neg { color:#f06060; } .neu { color:#7c83f5; }
.warn{ color:#f59e0b; }

[data-testid="stSidebar"] { background:#060810; border-right:1px solid #161829; }
.sb-header { font-family:'JetBrains Mono',monospace; font-size:15px; font-weight:700;
             color:#7c83f5; letter-spacing:2px; margin-bottom:18px; }
.sb-section { font-size:10px; letter-spacing:2px; text-transform:uppercase;
              color:#3a3f5c; margin:18px 0 8px; border-top:1px solid #161829; padding-top:12px; }

.live-badge { display:inline-flex; align-items:center; gap:6px; background:#0f1420;
              border:1px solid #22d3b0; border-radius:20px; padding:4px 14px;
              font-size:11px; color:#22d3b0; font-family:'JetBrains Mono',monospace; }
.dot { width:7px; height:7px; border-radius:50%; background:#22d3b0;
       animation:pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

.stale-badge { display:inline-flex; align-items:center; gap:6px; background:#0f1420;
               border:1px solid #f59e0b; border-radius:20px; padding:4px 14px;
               font-size:11px; color:#f59e0b; font-family:'JetBrains Mono',monospace; }

.hero-title { font-family:'JetBrains Mono',monospace; font-size:32px; font-weight:700;
              background:linear-gradient(120deg,#7c83f5 0%,#22d3b0 60%,#f59e0b 100%);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-sub { color:#2e3350; font-size:12px; letter-spacing:2px; margin-top:2px; }

.styled-table { width:100%; border-collapse:collapse; font-size:13px; }
.styled-table th { background:#0c0e1a; color:#4b5675; font-size:10px; letter-spacing:2px;
                   text-transform:uppercase; padding:10px 14px; border-bottom:1px solid #1e2236; }
.styled-table td { padding:9px 14px; border-bottom:1px solid #111525; }
.styled-table tr:last-child td { border-bottom:none; }

.stSelectbox label, .stSlider label, .stNumberInput label, .stCheckbox label,
.stRadio label { color:#4b5675 !important; font-size:11px !important;
                 letter-spacing:1.5px !important; text-transform:uppercase !important; }

.stButton > button {
    background:linear-gradient(135deg,#4f46e5,#7c83f5);
    color:#fff; border:none; border-radius:8px;
    padding:10px 20px; font-family:'JetBrains Mono',monospace;
    font-size:12px; font-weight:700; letter-spacing:1.5px; width:100%;
    transition:all .2s;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#7c83f5,#a5b4fc);
    transform:translateY(-1px);
    box-shadow:0 6px 22px rgba(124,131,245,.4);
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# STOCK UNIVERSE  (120+ tickers)
# ════════════════════════════════════════════════════════════════════
STOCKS = {
    "AAPL  – Apple":              "AAPL",
    "MSFT  – Microsoft":          "MSFT",
    "NVDA  – Nvidia":             "NVDA",
    "GOOGL – Alphabet A":         "GOOGL",
    "GOOG  – Alphabet C":         "GOOG",
    "META  – Meta Platforms":     "META",
    "AMZN  – Amazon":             "AMZN",
    "TSLA  – Tesla":              "TSLA",
    "AVGO  – Broadcom":           "AVGO",
    "ORCL  – Oracle":             "ORCL",
    "AMD   – AMD":                "AMD",
    "INTC  – Intel":              "INTC",
    "QCOM  – Qualcomm":           "QCOM",
    "AMAT  – Applied Materials":  "AMAT",
    "MU    – Micron":             "MU",
    "LRCX  – Lam Research":       "LRCX",
    "KLAC  – KLA Corp":           "KLAC",
    "MRVL  – Marvell Tech":       "MRVL",
    "SMCI  – Super Micro":        "SMCI",
    "ARM   – Arm Holdings":       "ARM",
    "CRM   – Salesforce":         "CRM",
    "NOW   – ServiceNow":         "NOW",
    "ADBE  – Adobe":              "ADBE",
    "SNOW  – Snowflake":          "SNOW",
    "PLTR  – Palantir":           "PLTR",
    "UBER  – Uber":               "UBER",
    "LYFT  – Lyft":               "LYFT",
    "SHOP  – Shopify":            "SHOP",
    "DDOG  – Datadog":            "DDOG",
    "ZS    – Zscaler":            "ZS",
    "CRWD  – CrowdStrike":        "CRWD",
    "OKTA  – Okta":               "OKTA",
    "MDB   – MongoDB":            "MDB",
    "NET   – Cloudflare":         "NET",
    "TWLO  – Twilio":             "TWLO",
    "GTLB  – GitLab":             "GTLB",
    "JPM   – JPMorgan":           "JPM",
    "BAC   – Bank of America":    "BAC",
    "WFC   – Wells Fargo":        "WFC",
    "GS    – Goldman Sachs":      "GS",
    "MS    – Morgan Stanley":     "MS",
    "BLK   – BlackRock":          "BLK",
    "V     – Visa":               "V",
    "MA    – Mastercard":         "MA",
    "PYPL  – PayPal":             "PYPL",
    "SQ    – Block":              "SQ",
    "AXP   – American Express":   "AXP",
    "C     – Citigroup":          "C",
    "BRK-B – Berkshire B":        "BRK-B",
    "SCHW  – Schwab":             "SCHW",
    "COF   – Capital One":        "COF",
    "JNJ   – Johnson & Johnson":  "JNJ",
    "UNH   – UnitedHealth":       "UNH",
    "LLY   – Eli Lilly":          "LLY",
    "PFE   – Pfizer":             "PFE",
    "MRK   – Merck":              "MRK",
    "ABBV  – AbbVie":             "ABBV",
    "BMY   – Bristol Myers":      "BMY",
    "AMGN  – Amgen":              "AMGN",
    "GILD  – Gilead":             "GILD",
    "CVS   – CVS Health":         "CVS",
    "TMO   – Thermo Fisher":      "TMO",
    "DHR   – Danaher":            "DHR",
    "ISRG  – Intuitive Surgical": "ISRG",
    "REGN  – Regeneron":          "REGN",
    "VRTX  – Vertex Pharma":      "VRTX",
    "WMT   – Walmart":            "WMT",
    "COST  – Costco":             "COST",
    "TGT   – Target":             "TGT",
    "HD    – Home Depot":         "HD",
    "LOW   – Lowe's":             "LOW",
    "NKE   – Nike":               "NKE",
    "MCD   – McDonald's":         "MCD",
    "SBUX  – Starbucks":          "SBUX",
    "CMG   – Chipotle":           "CMG",
    "YUM   – Yum Brands":         "YUM",
    "PG    – Procter & Gamble":   "PG",
    "KO    – Coca-Cola":          "KO",
    "PEP   – PepsiCo":            "PEP",
    "MDLZ  – Mondelez":           "MDLZ",
    "XOM   – ExxonMobil":         "XOM",
    "CVX   – Chevron":            "CVX",
    "COP   – ConocoPhillips":     "COP",
    "SLB   – SLB":                "SLB",
    "OXY   – Occidental":         "OXY",
    "CAT   – Caterpillar":        "CAT",
    "DE    – Deere":              "DE",
    "GE    – GE Aerospace":       "GE",
    "BA    – Boeing":             "BA",
    "RTX   – Raytheon":           "RTX",
    "LMT   – Lockheed Martin":    "LMT",
    "UPS   – UPS":                "UPS",
    "FDX   – FedEx":              "FDX",
    "SPY   – S&P 500 ETF":        "SPY",
    "QQQ   – Nasdaq-100 ETF":     "QQQ",
    "IWM   – Russell 2000 ETF":   "IWM",
    "DIA   – Dow Jones ETF":      "DIA",
    "VTI   – Total Market ETF":   "VTI",
    "VOO   – Vanguard S&P ETF":   "VOO",
    "ARKK  – ARK Innovation":     "ARKK",
    "SQQQ  – 3x Inverse QQQ":     "SQQQ",
    "TQQQ  – 3x Leveraged QQQ":   "TQQQ",
    "IBIT  – iShares BTC ETF":    "IBIT",
    "FBTC  – Fidelity BTC ETF":   "FBTC",
    "MSTR  – MicroStrategy":      "MSTR",
    "COIN  – Coinbase":           "COIN",
    "AMT   – American Tower":     "AMT",
    "PLD   – Prologis":           "PLD",
    "O     – Realty Income":      "O",
    "NEE   – NextEra Energy":     "NEE",
    "DUK   – Duke Energy":        "DUK",
    "TSM   – TSMC":               "TSM",
    "ASML  – ASML":               "ASML",
    "SAP   – SAP SE":             "SAP",
    "NVO   – Novo Nordisk":       "NVO",
    "BABA  – Alibaba":            "BABA",
    "JD    – JD.com":             "JD",
    "BIDU  – Baidu":              "BIDU",
    "SE    – Sea Limited":        "SE",
    "MELI  – MercadoLibre":       "MELI",
    "NU    – Nubank":             "NU",
    "RDDT  – Reddit":             "RDDT",
    "RBLX  – Roblox":             "RBLX",
    "SNAP  – Snap":               "SNAP",
    "PINS  – Pinterest":          "PINS",
    "SPOT  – Spotify":            "SPOT",
    "NFLX  – Netflix":            "NFLX",
    "DIS   – Disney":             "DIS",
    "CMCSA – Comcast":            "CMCSA",
    "T     – AT&T":               "T",
    "VZ    – Verizon":            "VZ",
}

PERIOD_MAP = {
    "1 Month":      "1mo",
    "3 Months":     "3mo",
    "6 Months":     "6mo",
    "1 Year":       "1y",
    "2 Years":      "2y",
    "3 Years":      "3y",
    "5 Years":      "5y",
    "10 Years":     "10y",
    "Max":          "max",
    "Custom Range": "custom",
}

CHART_BG = "#080a10"
PLOT_BG  = "#0c0e1a"
GRID_COL = "#161829"
FONT_COL = "#8b90a8"

# ════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════
for k, v in [
    ("last_fetch", 0), ("cached_df", None), ("cached_ticker", ""),
    ("cached_period", ""), ("refresh_counter", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════
def fetch_stock_data(ticker, period="2y", start=None, end=None):
    stock = yf.Ticker(ticker)
    if period == "custom" and start and end:
        return stock.history(start=start, end=end)
    return stock.history(period=period)


def log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()


def run_monte_carlo(last_price, mu, sigma, trading_days, n_sims, dt=1/252):
    paths = np.empty((trading_days + 1, n_sims))
    paths[0] = last_price
    rand = np.random.standard_normal((trading_days, n_sims))
    for t in range(1, trading_days + 1):
        paths[t] = paths[t-1] * np.exp((mu - .5*sigma**2)*dt + sigma*np.sqrt(dt)*rand[t-1])
    return paths


def var_cvar(final_prices, last_price, confidence=.95):
    ret = (final_prices - last_price) / last_price
    v   = np.percentile(ret, (1 - confidence) * 100)
    cv  = ret[ret <= v].mean()
    return v, cv

def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/window, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_stochastic(high, low, close, k_window=14, d_window=3):
    lowest_low = low.rolling(k_window).min()
    highest_high = high.rolling(k_window).max()
    denom = (highest_high - lowest_low).replace(0, np.nan)
    k = 100 * (close - lowest_low) / denom
    d = k.rolling(d_window).mean()
    return k.fillna(50), d.fillna(50)


def compute_cmf(high, low, close, volume, window=21):
    denom = (high - low).replace(0, np.nan)
    mfm = ((close - low) - (high - close)) / denom
    mfv = mfm * volume
    cmf = mfv.rolling(window).sum() / volume.rolling(window).sum()
    return cmf.fillna(0)


def grid_layout(title, height=1040):
    return dict(
        title=dict(text=title, font=dict(family="JetBrains Mono", size=16, color="#dde1f0")),
        paper_bgcolor=CHART_BG, plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Outfit"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COL),
        height=height,
        margin=dict(l=10, r=10, t=70, b=10),
    )


def resample_ohlc(source_df, rule):
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    if "Volume" in source_df.columns:
        agg["Volume"] = "sum"
    res = source_df.resample(rule).agg(agg).dropna(how="any")
    return res


def chart_layout(title, height=380):
    return dict(
        title=dict(text=title, font=dict(family="JetBrains Mono", size=13, color="#dde1f0")),
        paper_bgcolor=CHART_BG, plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Outfit"),
        xaxis=dict(gridcolor=GRID_COL, zeroline=False, showspikes=True,
                   spikecolor="#7c83f5", spikedash="dot"),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False, showspikes=True,
                   spikecolor="#7c83f5", spikedash="dot"),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COL),
        height=height,
        margin=dict(l=10, r=10, t=46, b=10),
    )


def kpi_card(col, label, value, delta=None, cls="neu"):
    delta_html = f'<div class="kdelta {cls}">{delta}</div>' if delta else ""
    col.markdown(
        f'<div class="kpi">'
        f'<div class="klabel">{label}</div>'
        f'<div class="kval {cls}">{value}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-header">⚡ MC PRO CONTROLS</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">STOCK SELECTOR</div>', unsafe_allow_html=True)
    stock_labels  = sorted(STOCKS.keys())
    default_idx   = stock_labels.index("AAPL  – Apple")
    selected_label = st.selectbox("Choose from 120+ Stocks", stock_labels, index=default_idx)
    ticker = STOCKS[selected_label]

    custom_ticker = st.text_input("Or type any custom ticker", placeholder="e.g. RDDT, NVDL, BTC-USD…")
    if custom_ticker.strip():
        ticker = custom_ticker.strip().upper()

    st.markdown('<div class="sb-section">HISTORICAL WINDOW</div>', unsafe_allow_html=True)
    period_label = st.selectbox("Time Period", list(PERIOD_MAP.keys()), index=4)
    period_key   = PERIOD_MAP[period_label]

    custom_start = custom_end = None
    if period_key == "custom":
        col_a, col_b = st.columns(2)
        custom_start = col_a.date_input("Start", value=date.today() - timedelta(days=730))
        custom_end   = col_b.date_input("End",   value=date.today())

    st.markdown('<div class="sb-section">SIMULATION PARAMS</div>', unsafe_allow_html=True)
    n_simulations = st.select_slider("Simulations", [100, 500, 1000, 2000, 5000, 10000], value=1000)
    horizon_days  = st.slider("Forecast Horizon (trading days)", 5, 504, 63,
                               help="63≈3mo · 126≈6mo · 252≈1yr · 504≈2yr")
    conf_pct      = st.slider("Confidence Level (%)", 90, 99, 95)

    st.markdown('<div class="sb-section">PARAM OVERRIDE</div>', unsafe_allow_html=True)
    use_custom_params = st.checkbox("Override μ / σ manually")
    custom_mu = custom_sigma = None
    if use_custom_params:
        custom_mu    = st.number_input("Annual Drift μ",       value=0.10, step=0.01, format="%.3f")
        custom_sigma = st.number_input("Annual Volatility σ",  value=0.25, step=0.01, format="%.3f")

    st.markdown('<div class="sb-section">LIVE DATA</div>', unsafe_allow_html=True)
    continuous_mode = st.checkbox(
        "Continuous Simulation (auto-refresh until you stop it)", value=True
    )
    refresh_secs   = st.select_slider("Refresh Interval",
                                      options=[15, 30, 60, 120, 300, 600],
                                      value=60,
                                      format_func=lambda x: f"{x}s" if x < 60 else f"{x//60}m",
                                      disabled=not continuous_mode)
    manual_refresh = st.button("🔄  REFRESH NOW")

    st.markdown('<div class="sb-section">CHART OPTIONS</div>', unsafe_allow_html=True)
    show_candle    = st.checkbox("Candlestick",         value=True)
    show_volume    = st.checkbox("Volume Bars",         value=True)
    show_bbands    = st.checkbox("Bollinger Bands",     value=True)
    show_sma       = st.checkbox("SMA 50 / 200",        value=True)
    show_macd      = st.checkbox("MACD",                value=True)
    show_rsi       = st.checkbox("RSI (14)",            value=True)
    n_paths_show   = st.slider("Visible MC Paths", 50, 500, 150)

# ════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════
hdr1, hdr2 = st.columns([3, 1])
with hdr1:
    st.markdown(
        '<div class="hero-title">⚡ QUANTUM PULSE ATLAS</div>'
        '<div class="hero-sub">QUANTITATIVE STOCK FORECASTING · GBM · LIVE AUTO-REFRESH</div>',
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════
# DATA FETCH  (smart cache + auto-refresh)
# ════════════════════════════════════════════════════════════════════
now       = time.time()
cache_key = f"{ticker}|{period_key}|{custom_start}|{custom_end}"
need_ref  = (
    manual_refresh
    or st.session_state.cached_df is None
    or st.session_state.cached_ticker != cache_key
    or (continuous_mode and (now - st.session_state.last_fetch) >= refresh_secs)
)

if need_ref:
    with st.spinner(f"⚡ Fetching {ticker} from Yahoo Finance…"):
        try:
            df_raw = fetch_stock_data(ticker, period_key, custom_start, custom_end)
            if df_raw.empty:
                st.error(f"No data found for **{ticker}**.")
                st.stop()
            st.session_state.cached_df      = df_raw
            st.session_state.cached_ticker  = cache_key
            st.session_state.last_fetch     = now
            st.session_state.refresh_counter += 1
        except Exception as e:
            st.error(f"Fetch error: {e}")
            if st.session_state.cached_df is None:
                st.stop()

df        = st.session_state.cached_df
fetch_age = int(time.time() - st.session_state.last_fetch)
is_fresh  = fetch_age < 120

with hdr2:
    ts = datetime.fromtimestamp(st.session_state.last_fetch).strftime("%H:%M:%S")
    if is_fresh:
        st.markdown(
            f'<div style="text-align:right;margin-top:12px">'
            f'<span class="live-badge"><span class="dot"></span>LIVE · {ts}</span><br>'
            f'<small style="color:#2e3350;font-size:10px">Refresh #{st.session_state.refresh_counter} · {ticker}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="text-align:right;margin-top:12px">'
            f'<span class="stale-badge">⏱ {fetch_age}s AGO</span></div>',
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════
# ANALYTICS
# ════════════════════════════════════════════════════════════════════
prices  = df["Close"].squeeze()
volumes = df["Volume"].squeeze() if "Volume" in df.columns else None

log_ret    = log_returns(prices)
mu_d       = float(log_ret.mean())
sigma_d    = float(log_ret.std())
mu_ann     = mu_d * 252
sigma_ann  = sigma_d * np.sqrt(252)

if use_custom_params and custom_mu is not None:
    mu_ann    = custom_mu;  sigma_ann = custom_sigma
    mu_d      = mu_ann / 252; sigma_d   = sigma_ann / np.sqrt(252)

last_price   = float(prices.iloc[-1])
prev_price   = float(prices.iloc[-2]) if len(prices) > 1 else last_price
daily_chg    = (last_price - prev_price) / prev_price * 100

yr_prices    = prices[prices.index.year == datetime.now().year]
ytd_start    = float(yr_prices.iloc[0]) if len(yr_prices) else float(prices.iloc[0])
ytd_ret      = (last_price - ytd_start) / ytd_start * 100
max_dd       = float(((prices / prices.cummax()) - 1).min() * 100)
sharpe       = mu_ann / sigma_ann if sigma_ann != 0 else 0.0

# Technical
ema12  = prices.ewm(span=12, adjust=False).mean()
ema26  = prices.ewm(span=26, adjust=False).mean()
macd_l = ema12 - ema26
sig_l  = macd_l.ewm(span=9, adjust=False).mean()
macd_h = macd_l - sig_l

dlt   = prices.diff()
gain  = dlt.clip(lower=0).ewm(com=13, adjust=False).mean()
loss  = (-dlt.clip(upper=0)).ewm(com=13, adjust=False).mean()
rsi   = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

sma20  = prices.rolling(20).mean()
std20  = prices.rolling(20).std()
bb_up  = sma20 + 2*std20
bb_dn  = sma20 - 2*std20
sma50  = prices.rolling(50).mean()
sma200 = prices.rolling(200).mean()

# Monte Carlo
np.random.seed(None)
with st.spinner("Running Monte Carlo…"):
    paths = run_monte_carlo(last_price, mu_d, sigma_d, horizon_days, n_simulations)

final_p    = paths[-1]
med_p      = float(np.median(final_p))
mean_p     = float(final_p.mean())
p5         = float(np.percentile(final_p, 5))
p25        = float(np.percentile(final_p, 25))
p75        = float(np.percentile(final_p, 75))
p95        = float(np.percentile(final_p, 95))
prob_prof  = float((final_p > last_price).mean() * 100)
var_, cvar_ = var_cvar(final_p, last_price, conf_pct/100)

quantile_levels = [5, 25, 50, 75, 95]
mc_quantiles = {
    f"P{lvl}": float(np.percentile(final_p, lvl))
    for lvl in quantile_levels
}
thresholds = np.linspace(last_price * 0.7, last_price * 1.4, 14)
threshold_probs = [(final_p >= th).mean() * 100 for th in thresholds]
mean_path = paths.mean(axis=1)
std_path = paths.std(axis=1)
p95_path = np.percentile(paths, 95, axis=1)
p5_path = np.percentile(paths, 5, axis=1)
path_width = p95_path - p5_path
above_today = (paths >= last_price).mean(axis=1) * 100
cdf_vals = np.sort(final_p)
cdf_pct = np.arange(1, len(final_p) + 1) / len(final_p)

horizon_targets = [5, 10, 21, 42, 63, 126, 189, 252, 378, 504]
horizon_stats = {}
for h in horizon_targets:
    snapshot = run_monte_carlo(last_price, mu_d, sigma_d, h, 500)[-1]
    ret = (snapshot - last_price) / last_price
    var_h = float(np.percentile(ret, (1 - conf_pct / 100) * 100))
    cvar_h = float(ret[ret <= var_h].mean())
    horizon_stats[h] = {
        "mean": float(snapshot.mean()),
        "median": float(np.median(snapshot)),
        "std": float(snapshot.std()),
        "p5": float(np.percentile(snapshot, 5)),
        "p95": float(np.percentile(snapshot, 95)),
        "prob_profit": float((snapshot > last_price).mean() * 100),
        "var": var_h,
        "cvar": cvar_h,
        "ratio": float(np.percentile(snapshot, 95)) / last_price if last_price else 0.0,
        "spread": float(np.percentile(snapshot, 95)) - float(np.percentile(snapshot, 5)),
        "spread_pct": ((float(np.percentile(snapshot, 95)) - float(np.percentile(snapshot, 5))) / last_price * 100)
                        if last_price else 0,
        "tail_prob": float((snapshot <= last_price * 0.9).mean() * 100),
    }

has_ohlc = all(c in df.columns for c in ["Open", "High", "Low", "Close"])
daily_range = (df["High"] - df["Low"]) if has_ohlc else pd.Series(0.0, index=prices.index)
typical_price = ((df["High"] + df["Low"] + df["Close"]) / 3) if has_ohlc else prices
vwap = None
if volumes is not None and has_ohlc:
    cum_vol = volumes.cumsum()
    cum_vwap = ((typical_price * volumes).cumsum())
    vwap = cum_vwap / cum_vol.replace(0, np.nan)
volume_ma21 = volumes.rolling(21).mean() if volumes is not None else None
volume_range_ratio = None
if volumes is not None:
    price_range_safe = daily_range.replace(0, np.nan)
    volume_range_ratio = (volumes / price_range_safe).replace([np.inf, -np.inf], np.nan).fillna(0)
range_52w = (prices / prices.rolling(252).max() - 1) * 100
returns = prices.pct_change().dropna()
weekday_returns = returns.groupby(returns.index.weekday).mean() * 100
monthly_volatility = returns.groupby(returns.index.month).std() * 100
range30 = daily_range.rolling(30).mean() if has_ohlc else None
volume30 = volumes.rolling(30).mean() if volumes is not None else None

rsi5 = compute_rsi(prices, 5)
rsi14 = compute_rsi(prices, 14)
macd_spread = macd_l - sig_l
bb_width = ((bb_up - bb_dn) / sma20).replace([np.inf, -np.inf], np.nan) * 100
bb_width = bb_width.fillna(0)
stoch_k = stoch_d = pd.Series(dtype=float)
cmf21 = pd.Series(dtype=float)
if has_ohlc:
    stoch_k, stoch_d = compute_stochastic(df["High"], df["Low"], prices)
    if volumes is not None:
        cmf21 = compute_cmf(df["High"], df["Low"], prices, volumes, 21)
rolling_skew = (log_ret * 100).rolling(21).skew()
rolling_kurt = (log_ret * 100).rolling(21).kurt()

# ════════════════════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════════════════════
kpi_data = [
    ("LAST PRICE",        f"${last_price:.2f}",   f"{daily_chg:+.2f}% today",
     "pos" if daily_chg >= 0 else "neg"),
    ("YTD RETURN",        f"{ytd_ret:+.1f}%",     None,
     "pos" if ytd_ret >= 0 else "neg"),
    ("MC MEDIAN",         f"${med_p:.2f}",
     f"{(med_p-last_price)/last_price*100:+.1f}%",
     "pos" if med_p >= last_price else "neg"),
    ("P(PROFIT)",         f"{prob_prof:.1f}%",    f"{horizon_days}d horizon",
     "pos" if prob_prof >= 55 else "neg" if prob_prof < 45 else "warn"),
    (f"VaR {conf_pct}%",  f"{var_*100:.2f}%",     "worst-case loss",  "neg"),
    (f"CVaR {conf_pct}%", f"{cvar_*100:.2f}%",    "expected shortfall","neg"),
    ("SHARPE",            f"{sharpe:.2f}",         "annualised (rf=0)",
     "pos" if sharpe > 1 else "warn" if sharpe > 0 else "neg"),
    ("ANN VOL",           f"{sigma_ann*100:.1f}%", "1-yr volatility",  "neu"),
    ("MAX DRAWDOWN",      f"{max_dd:.1f}%",        "historical",       "neg"),
]
cols = st.columns(len(kpi_data))
for col, (lbl, val, delta, cls) in zip(cols, kpi_data):
    kpi_card(col, lbl, val, delta, cls)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab_mc, tab_price, tab_tech, tab_risk, tab_stats = st.tabs([
    "🎲 Monte Carlo", "📈 Price & Volume", "🔬 Technical", "⚠️ Risk", "📊 Statistics"
])

# ─────────────── TAB 1 · MONTE CARLO ────────────────────────────
with tab_mc:
    t_ax = np.arange(horizon_days + 1)
    fig_mc = go.Figure()

    idx = np.random.choice(n_simulations, min(n_paths_show, n_simulations), replace=False)
    for i in idx:
        fig_mc.add_trace(go.Scatter(
            x=t_ax, y=paths[:, i], mode="lines",
            line=dict(width=0.35, color="rgba(124,131,245,0.11)"),
            showlegend=False, hoverinfo="skip",
        ))

    # Uncertainty cone fill
    cone_hi = np.percentile(paths, 95, axis=1)
    cone_lo = np.percentile(paths, 5,  axis=1)
    fig_mc.add_trace(go.Scatter(
        x=np.concatenate([t_ax, t_ax[::-1]]),
        y=np.concatenate([cone_hi, cone_lo[::-1]]),
        fill="toself", fillcolor="rgba(124,131,245,0.05)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    for pct, lbl, c in [(95,"P95","#22d3b0"),(75,"P75","#6ee7d0"),
                         (50,"Median","#7c83f5"),(25,"P25","#fb923c"),(5,"P5","#f06060")]:
        fig_mc.add_trace(go.Scatter(
            x=t_ax, y=np.percentile(paths, pct, axis=1),
            name=lbl, mode="lines", line=dict(width=2, color=c),
        ))
    fig_mc.add_hline(y=last_price, line_dash="dot", line_color="#8b90a8",
                     annotation_text=f"Now: ${last_price:.2f}",
                     annotation_font_color="#8b90a8")
    fig_mc.update_layout(**chart_layout(
        f"{ticker} · Monte Carlo ({n_simulations:,} paths · {horizon_days} trading days)", 460))
    fig_mc.update_xaxes(title_text="Trading Days Ahead")
    fig_mc.update_yaxes(title_text="Price (USD)")
    st.plotly_chart(fig_mc, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=final_p, nbinsx=100,
            marker=dict(color="#7c83f5", opacity=.8),
        ))
        for v, lbl, c in [(last_price,"Now","#8b90a8"),(p5,"5%","#f06060"),
                           (med_p,"Median","#7c83f5"),(p95,"95%","#22d3b0")]:
            fig_dist.add_vline(x=v, line_dash="dash", line_color=c,
                               annotation_text=lbl, annotation_font_color=c)
        fig_dist.update_layout(**chart_layout("Final Price Distribution", 340))
        st.plotly_chart(fig_dist, use_container_width=True)

    with c2:
        pcts   = [1,5,10,25,50,75,90,95,99]
        pvals  = [float(np.percentile(final_p, p)) for p in pcts]
        colors = ["#ef4444","#f06060","#fb923c","#fbbf24","#7c83f5",
                  "#6ee7d0","#34d399","#22d3b0","#10b981"]
        fig_bar = go.Figure(go.Bar(
            x=[f"P{p}" for p in pcts], y=pvals, marker_color=colors,
            text=[f"${v:.2f}" for v in pvals], textposition="outside",
        ))
        fig_bar.add_hline(y=last_price, line_dash="dot", line_color="#8b90a8")
        fig_bar.update_layout(**chart_layout("Price Percentiles at Horizon", 340))
        st.plotly_chart(fig_bar, use_container_width=True)

    sim_ret = (final_p - last_price) / last_price * 100
    fig_pl = go.Figure()
    fig_pl.add_trace(go.Histogram(x=sim_ret[sim_ret>0],  nbinsx=60,
                                  marker_color="#22d3b0", opacity=.75, name="Profit"))
    fig_pl.add_trace(go.Histogram(x=sim_ret[sim_ret<=0], nbinsx=60,
                                  marker_color="#f06060", opacity=.75, name="Loss"))
    fig_pl.add_vline(x=0, line_color="#8b90a8", line_dash="dot")
    fig_pl.add_vline(x=var_*100, line_color="#f59e0b", line_dash="dash",
                     annotation_text=f"VaR {conf_pct}%")
    fig_pl.update_layout(**chart_layout("Simulated Return Distribution (%)", 320))
    st.plotly_chart(fig_pl, use_container_width=True)

    fig_mc_grid = make_subplots(
        rows=4, cols=2,
        subplot_titles=[
            "Final Price CDF", "Probability vs Threshold",
            "Mean ± Std Path", "Path Dispersion (Std)",
            "Quantile Ladder", "Return Box (%)",
            "P95-P5 Width", "% Paths ≥ Today",
        ],
        vertical_spacing=0.06, horizontal_spacing=0.05,
    )
    fig_mc_grid.add_trace(go.Scatter(
        x=cdf_vals, y=cdf_pct, mode="lines",
        line=dict(color="#7c83f5", width=2),
    ), row=1, col=1)
    fig_mc_grid.add_trace(go.Scatter(
        x=thresholds, y=threshold_probs, mode="lines+markers",
        line=dict(color="#22d3b0", width=1.75), marker=dict(color="#22d3b0", size=6),
    ), row=1, col=2)
    upper = mean_path + std_path
    lower = mean_path - std_path
    fig_mc_grid.add_trace(go.Scatter(
        x=np.concatenate([t_ax, t_ax[::-1]]),
        y=np.concatenate([upper, lower[::-1]]),
        fill="toself", fillcolor="rgba(34,211,176,0.08)",
        line=dict(width=0), showlegend=False,
    ), row=2, col=1)
    fig_mc_grid.add_trace(go.Scatter(
        x=t_ax, y=mean_path,
        line=dict(color="#22d3b0", width=2, shape="spline"),
    ), row=2, col=1)
    fig_mc_grid.add_trace(go.Scatter(
        x=t_ax, y=std_path, line=dict(color="#fb923c", width=1.5),
    ), row=2, col=2)
    fig_mc_grid.add_trace(go.Bar(
        x=list(mc_quantiles.keys()), y=list(mc_quantiles.values()),
        marker_color=["#f06060","#fb923c","#7c83f5","#6ee7d0","#22d3b0"],
        text=[f"${v:.2f}" for v in mc_quantiles.values()],
        textposition="outside",
    ), row=3, col=1)
    fig_mc_grid.add_trace(go.Box(
        y=sim_ret, marker_color="#7c83f5", boxmean="sd", name="Simulated Return (%)"
    ), row=3, col=2)
    fig_mc_grid.add_trace(go.Scatter(
        x=t_ax, y=path_width, line=dict(color="#fbbf24", width=1.5),
    ), row=4, col=1)
    fig_mc_grid.add_trace(go.Scatter(
        x=t_ax, y=above_today, line=dict(color="#22d3b0", width=1.5),
    ), row=4, col=2)
    fig_mc_grid.update_xaxes(title_text="Price (USD)", row=1, col=1)
    fig_mc_grid.update_yaxes(title_text="Probability", row=1, col=2)
    fig_mc_grid.update_yaxes(title_text="USD", row=3, col=1)
    fig_mc_grid.update_layout(**grid_layout(f"{ticker} · Monte Carlo Micro Metrics", height=1120))
    st.plotly_chart(fig_mc_grid, use_container_width=True)


# ─────────────── TAB 2 · PRICE & VOLUME ──────────────────────────
with tab_price:
    has_ohlc = all(c in df.columns for c in ["Open","High","Low","Close"])
    if show_candle and has_ohlc:
        rows      = 2 if (show_volume and volumes is not None) else 1
        rh        = [0.72, 0.28] if rows==2 else [1]
        specs     = [[{"type":"candlestick"}]] + ([[{"type":"bar"}]] if rows==2 else [])
        fig_cs    = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                                  row_heights=rh, vertical_spacing=0.03, specs=specs)

        fig_cs.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color="#22d3b0", decreasing_line_color="#f06060",
            name="OHLC",
        ), row=1, col=1)

        if show_bbands:
            for band, nm, c, d in [
                (bb_up,"BB Upper","#7c83f5","dot"),
                (sma20,"SMA 20",  "#f59e0b","solid"),
                (bb_dn,"BB Lower","#7c83f5","dot"),
            ]:
                fig_cs.add_trace(go.Scatter(x=prices.index, y=band, name=nm,
                                            line=dict(width=1, color=c, dash=d)), row=1, col=1)

        if show_sma:
            fig_cs.add_trace(go.Scatter(x=prices.index, y=sma50,  name="SMA 50",
                                        line=dict(width=1.3, color="#fb923c")), row=1, col=1)
            fig_cs.add_trace(go.Scatter(x=prices.index, y=sma200, name="SMA 200",
                                        line=dict(width=1.3, color="#f06060")), row=1, col=1)

        if show_volume and volumes is not None and rows==2:
            vc = ["#22d3b0" if c >= o else "#f06060"
                  for c, o in zip(df["Close"], df["Open"])]
            fig_cs.add_trace(go.Bar(x=df.index, y=volumes, marker_color=vc,
                                    opacity=.6, name="Volume"), row=2, col=1)

        fig_cs.update_layout(**chart_layout(f"{ticker} · OHLC Candlestick", 560))
        fig_cs.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig_cs, use_container_width=True)
    else:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=prices.index, y=prices, mode="lines",
            line=dict(color="#7c83f5", width=2),
            fill="tozeroy", fillcolor="rgba(124,131,245,0.07)",
        ))
        fig_line.update_layout(**chart_layout(f"{ticker} · Close Price", 420))
        st.plotly_chart(fig_line, use_container_width=True)

    # Monthly returns heatmap
    monthly = (prices.pct_change().dropna() * 100).resample("M").sum()
    mo_df   = monthly.to_frame("ret")
    mo_df["year"]  = mo_df.index.year
    mo_df["month"] = mo_df.index.month
    pivot   = mo_df.pivot(index="year", columns="month", values="ret")
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][
        :len(pivot.columns)
    ] if len(pivot.columns) <= 12 else list(range(1,13))

    fig_hm = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
        colorscale=[[0,"#ef4444"],[.5,"#1e2236"],[1,"#22d3b0"]],
        zmid=0,
        text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont=dict(size=9),
        hovertemplate="<b>%{y} %{x}</b><br>Return: %{z:.2f}%<extra></extra>",
        colorbar=dict(tickfont=dict(color=FONT_COL)),
    ))
    fig_hm.update_layout(**chart_layout(f"{ticker} · Monthly Returns Heatmap (%)", 300))
    st.plotly_chart(fig_hm, use_container_width=True)

    # Cumulative return
    cum_ret = (1 + prices.pct_change().fillna(0)).cumprod() - 1
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret * 100,
        mode="lines", line=dict(color="#22d3b0" if float(cum_ret.iloc[-1]) >= 0 else "#f06060", width=2),
        fill="tozeroy",
        fillcolor="rgba(34,211,176,0.07)" if float(cum_ret.iloc[-1]) >= 0 else "rgba(240,96,96,0.07)",
    ))
    fig_cum.add_hline(y=0, line_dash="dot", line_color="#4b5675")
    fig_cum.update_layout(**chart_layout("Cumulative Return (%)", 300))
    st.plotly_chart(fig_cum, use_container_width=True)

    if has_ohlc:
        ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
        ha_open = ((df["Open"].shift(1) + df["Close"].shift(1)) / 2).fillna(df["Open"])
        ha_high = pd.concat([df["High"], ha_open, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([df["Low"], ha_open, ha_close], axis=1).min(axis=1)
        heikin_df = pd.DataFrame({
            "Open": ha_open,
            "High": ha_high,
            "Low": ha_low,
            "Close": ha_close,
        }, index=df.index).dropna()

        candle_variants = [
            ("Daily Raw", df),
            ("Weekly", resample_ohlc(df, "W")),
            ("Biweekly", resample_ohlc(df, "2W")),
            ("10D Block", resample_ohlc(df, "10D")),
            ("Monthly", resample_ohlc(df, "M")),
            ("Quarterly", resample_ohlc(df, "Q")),
            ("21D / Month", resample_ohlc(df, "21D")),
            ("Heikin-Ashi", heikin_df),
        ]
        fig_candle_gallery = make_subplots(
            rows=4, cols=2,
            subplot_titles=[cfg[0] for cfg in candle_variants],
            vertical_spacing=0.06, horizontal_spacing=0.05,
        )
        for idx, (_, variant_df) in enumerate(candle_variants, start=1):
            if variant_df is None or variant_df.empty:
                continue
            row = (idx - 1) // 2 + 1
            col = (idx - 1) % 2 + 1
            fig_candle_gallery.add_trace(go.Candlestick(
                x=variant_df.index,
                open=variant_df["Open"],
                high=variant_df["High"],
                low=variant_df["Low"],
                close=variant_df["Close"],
                increasing_line_color="#22d3b0",
                decreasing_line_color="#f06060",
                name="",
                showlegend=False,
            ), row=row, col=col)
            fig_candle_gallery.update_xaxes(showgrid=False, row=row, col=col)
            fig_candle_gallery.update_yaxes(showgrid=True, row=row, col=col)
        fig_candle_gallery.update_layout(**grid_layout(f"{ticker} · Candlestick Gallery", height=1200))
        st.plotly_chart(fig_candle_gallery, use_container_width=True)

    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    weekday_vals = [weekday_returns.get(i, np.nan) for i in range(5)]
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_vols = [monthly_volatility.get(i, np.nan) for i in range(1, 13)]
    range30_series = range30.dropna() if range30 is not None else pd.Series(dtype=float)
    volume30_series = volume30.reindex(range30_series.index) if volume30 is not None else pd.Series(dtype=float)

    fig_price_grid = make_subplots(
        rows=4, cols=2,
        subplot_titles=[
            "Daily Range", "Close vs VWAP",
            "21d Volume", "Volume / Range Ratio",
            "Weekday Avg Return (%)", "Monthly Return Volatility (%)",
            "Distance from 52w High (%)", "Volume vs 30d Range",
        ],
        vertical_spacing=0.06, horizontal_spacing=0.05,
    )
    fig_price_grid.add_trace(go.Scatter(
        x=df.index, y=daily_range, line=dict(color="#7c83f5", width=1.5),
    ), row=1, col=1)
    fig_price_grid.add_trace(go.Scatter(
        x=df.index, y=prices, line=dict(color="#7c83f5", width=1.5), name="Close"
    ), row=1, col=2)
    if vwap is not None:
        fig_price_grid.add_trace(go.Scatter(
            x=vwap.index, y=vwap, line=dict(color="#6ee7d0", width=1.2), name="VWAP"
        ), row=1, col=2)
    if volume_ma21 is not None:
        fig_price_grid.add_trace(go.Scatter(
            x=volume_ma21.index, y=volume_ma21,
            line=dict(color="#fbbf24", width=1.5),
        ), row=2, col=1)
    if volume_range_ratio is not None:
        fig_price_grid.add_trace(go.Scatter(
            x=volume_range_ratio.index, y=volume_range_ratio,
            line=dict(color="#f59e0b", width=1.5),
        ), row=2, col=2)
    fig_price_grid.add_trace(go.Bar(
        x=weekday_labels, y=weekday_vals,
        marker_color="#7c83f5",
        text=[f"{v:.2f}%" if not np.isnan(v) else "" for v in weekday_vals],
        textposition="outside",
    ), row=3, col=1)
    fig_price_grid.add_trace(go.Bar(
        x=month_labels, y=month_vols,
        marker_color="#22d3b0",
        text=[f"{v:.2f}%" if not np.isnan(v) else "" for v in month_vols],
        textposition="outside",
    ), row=3, col=2)
    fig_price_grid.add_trace(go.Scatter(
        x=df.index, y=range_52w,
        line=dict(color="#f06060", width=1.5),
    ), row=4, col=1)
    if not range30_series.empty and not volume30_series.dropna().empty:
        fig_price_grid.add_trace(go.Scatter(
            x=range30_series, y=volume30_series,
            mode="markers", marker=dict(color="#fb923c", size=5, opacity=0.6),
        ), row=4, col=2)
    fig_price_grid.update_layout(**grid_layout(f"{ticker} · Price & Volume Micro Metrics", height=1120))
    st.plotly_chart(fig_price_grid, use_container_width=True)


# ─────────────── TAB 3 · TECHNICAL ──────────────────────────────
with tab_tech:
    if show_rsi:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, name="RSI(14)",
                                     line=dict(color="#7c83f5", width=1.5)))
        fig_rsi.add_hrect(y0=70,y1=100,fillcolor="rgba(240,96,96,.07)",line_width=0)
        fig_rsi.add_hrect(y0=0, y1=30, fillcolor="rgba(34,211,176,.07)",line_width=0)
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="#f06060",
                          annotation_text="Overbought 70")
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="#22d3b0",
                          annotation_text="Oversold 30")
        fig_rsi.update_layout(**chart_layout("RSI (14)", 280))
        fig_rsi.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_rsi, use_container_width=True)

    if show_macd:
        fig_m = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              row_heights=[.6,.4], vertical_spacing=0.04)
        fig_m.add_trace(go.Scatter(x=prices.index, y=prices, name="Price",
                                   line=dict(color="#7c83f5", width=1.5)), row=1, col=1)
        fig_m.add_trace(go.Scatter(x=macd_l.index, y=macd_l,  name="MACD",
                                   line=dict(color="#22d3b0",  width=1.5)), row=2, col=1)
        fig_m.add_trace(go.Scatter(x=sig_l.index,  y=sig_l,   name="Signal",
                                   line=dict(color="#f59e0b", width=1.2, dash="dash")), row=2, col=1)
        fig_m.add_trace(go.Bar(x=macd_h.index, y=macd_h,
                               marker_color=["#22d3b0" if v>=0 else "#f06060" for v in macd_h],
                               opacity=.6, name="Histogram"), row=2, col=1)
        fig_m.update_layout(**chart_layout("Price + MACD (12,26,9)", 400))
        st.plotly_chart(fig_m, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        rv21 = log_returns(prices).rolling(21).std() * np.sqrt(252) * 100
        rv63 = log_returns(prices).rolling(63).std() * np.sqrt(252) * 100
        fig_rv = go.Figure()
        fig_rv.add_trace(go.Scatter(x=rv21.index, y=rv21, name="21d Vol",
                                    line=dict(color="#f06060",width=1.5),
                                    fill="tozeroy",fillcolor="rgba(240,96,96,.06)"))
        fig_rv.add_trace(go.Scatter(x=rv63.index, y=rv63, name="63d Vol",
                                    line=dict(color="#7c83f5",width=1.5)))
        fig_rv.update_layout(**chart_layout("Realised Volatility (%)", 300))
        st.plotly_chart(fig_rv, use_container_width=True)

    with c2:
        rs_sharpe = (log_returns(prices).rolling(63).mean()*252) / \
                    (log_returns(prices).rolling(63).std()*np.sqrt(252))
        fig_rsh = go.Figure()
        fig_rsh.add_trace(go.Scatter(x=rs_sharpe.index, y=rs_sharpe,
                                     name="Rolling Sharpe 63d",
                                     line=dict(color="#22d3b0",width=1.5)))
        fig_rsh.add_hline(y=1,line_dash="dot",line_color="#f59e0b",annotation_text="Sharpe=1")
        fig_rsh.add_hline(y=0,line_dash="dot",line_color="#f06060")
        fig_rsh.update_layout(**chart_layout("63-Day Rolling Sharpe", 300))
        st.plotly_chart(fig_rsh, use_container_width=True)

    dd = (prices / prices.cummax() - 1) * 100
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=dd.index, y=dd, fill="tozeroy",
                                fillcolor="rgba(240,96,96,.15)",
                                line=dict(color="#f06060",width=1.5), name="Drawdown"))
    fig_dd.update_layout(**chart_layout("Historical Drawdown (%)", 280))
    st.plotly_chart(fig_dd, use_container_width=True)

    # OBV
    if volumes is not None:
        obv = (np.sign(prices.diff()) * volumes).fillna(0).cumsum()
        fig_obv = go.Figure()
        fig_obv.add_trace(go.Scatter(x=obv.index, y=obv, name="OBV",
                                     line=dict(color="#fb923c",width=1.5),
                                     fill="tozeroy",fillcolor="rgba(251,146,60,.06)"))
        fig_obv.update_layout(**chart_layout("On-Balance Volume (OBV)", 260))
        st.plotly_chart(fig_obv, use_container_width=True)

    fig_tech_grid = make_subplots(
        rows=4, cols=2,
        subplot_titles=[
            "RSI Comparison", "MACD Signal Spread",
            "Bollinger Width (%)", "Stochastic %K / %D",
            "Rolling Skewness (21d)", "Rolling Kurtosis (21d)",
            "Chaikin Money Flow (21d)", "EMA12 - EMA26 Gap",
        ],
        vertical_spacing=0.06, horizontal_spacing=0.05,
    )
    fig_tech_grid.add_trace(go.Scatter(
        x=rsi5.index, y=rsi5, line=dict(color="#22d3b0", width=1.5), name="RSI 5"
    ), row=1, col=1)
    fig_tech_grid.add_trace(go.Scatter(
        x=rsi14.index, y=rsi14, line=dict(color="#fb923c", width=1.5), name="RSI 14"
    ), row=1, col=1)
    fig_tech_grid.add_trace(go.Scatter(
        x=macd_spread.index, y=macd_spread, line=dict(color="#7c83f5", width=1.5),
    ), row=1, col=2)
    fig_tech_grid.add_trace(go.Scatter(
        x=bb_width.index, y=bb_width, line=dict(color="#6ee7d0", width=1.5),
    ), row=2, col=1)
    if not stoch_k.empty:
        fig_tech_grid.add_trace(go.Scatter(
            x=stoch_k.index, y=stoch_k, line=dict(color="#22d3b0", width=1.3), name="%K"
        ), row=2, col=2)
    if not stoch_d.empty:
        fig_tech_grid.add_trace(go.Scatter(
            x=stoch_d.index, y=stoch_d, line=dict(color="#fbbf24", width=1.3), name="%D"
        ), row=2, col=2)
    fig_tech_grid.add_trace(go.Scatter(
        x=rolling_skew.index, y=rolling_skew, line=dict(color="#f06060", width=1.5),
    ), row=3, col=1)
    fig_tech_grid.add_trace(go.Scatter(
        x=rolling_kurt.index, y=rolling_kurt, line=dict(color="#22d3b0", width=1.5),
    ), row=3, col=2)
    if not cmf21.empty:
        fig_tech_grid.add_trace(go.Scatter(
            x=cmf21.index, y=cmf21, line=dict(color="#34d399", width=1.5),
        ), row=4, col=1)
    ema_gap = (ema12 - ema26)
    fig_tech_grid.add_trace(go.Scatter(
        x=ema_gap.index, y=ema_gap, line=dict(color="#fb923c", width=1.5),
    ), row=4, col=2)
    fig_tech_grid.update_layout(**grid_layout(f"{ticker} · Technical Micro Metrics", height=1120))
    st.plotly_chart(fig_tech_grid, use_container_width=True)


# ─────────────── TAB 4 · RISK ────────────────────────────────────
with tab_risk:
    c1, c2 = st.columns(2)
    with c1:
        confs  = list(range(90, 100))
        vars_  = [var_cvar(final_p, last_price, c/100)[0]*100 for c in confs]
        cvars_ = [var_cvar(final_p, last_price, c/100)[1]*100 for c in confs]
        fig_v  = go.Figure()
        fig_v.add_trace(go.Scatter(x=confs, y=vars_,  name="VaR",
                                   mode="lines+markers", line=dict(color="#f59e0b",width=2)))
        fig_v.add_trace(go.Scatter(x=confs, y=cvars_, name="CVaR/ES",
                                   mode="lines+markers", line=dict(color="#f06060",width=2)))
        fig_v.update_layout(**chart_layout("VaR & CVaR across Confidence Levels (%)", 340))
        fig_v.update_xaxes(title_text="Confidence Level (%)")
        st.plotly_chart(fig_v, use_container_width=True)

    with c2:
        scenarios = {
            "Bear −40%": last_price*.60, "Bear −30%": last_price*.70,
            "Bear −20%": last_price*.80, "Bear −10%": last_price*.90,
            "Flat":      last_price,
            "Bull +10%": last_price*1.10,"Bull +20%": last_price*1.20,
            "Bull +30%": last_price*1.30,"Bull +40%": last_price*1.40,
        }
        sc_probs = {
            k: (final_p >= v if "Bull" in k or k=="Flat" else final_p <= v).mean()*100
            for k, v in scenarios.items()
        }
        colors_sc = ["#f06060","#f06060","#f06060","#f06060",
                     "#7c83f5","#22d3b0","#22d3b0","#22d3b0","#22d3b0"]
        fig_sc = go.Figure(go.Bar(
            x=list(sc_probs.keys()), y=list(sc_probs.values()),
            marker_color=colors_sc,
            text=[f"{v:.1f}%" for v in sc_probs.values()], textposition="outside",
        ))
        fig_sc.update_layout(**chart_layout("Scenario Probability at Horizon", 340))
        st.plotly_chart(fig_sc, use_container_width=True)

    # Horizon fan
    horizons = horizon_targets
    med_l = [horizon_stats[h]["median"] for h in horizons]
    p5_l = [horizon_stats[h]["p5"] for h in horizons]
    p95_l = [horizon_stats[h]["p95"] for h in horizons]

    fig_fan = go.Figure()
    fig_fan.add_trace(go.Scatter(
        x=horizons+horizons[::-1], y=p95_l+p5_l[::-1],
        fill="toself", fillcolor="rgba(124,131,245,0.09)",
        line=dict(width=0), showlegend=False,
    ))
    fig_fan.add_trace(go.Scatter(x=horizons, y=p95_l, name="P95",
                                 line=dict(color="#22d3b0",width=1.5,dash="dash")))
    fig_fan.add_trace(go.Scatter(x=horizons, y=med_l,  name="Median",
                                 line=dict(color="#7c83f5",width=2.5)))
    fig_fan.add_trace(go.Scatter(x=horizons, y=p5_l,   name="P5",
                                 line=dict(color="#f06060",width=1.5,dash="dash")))
    fig_fan.add_hline(y=last_price, line_dash="dot", line_color="#8b90a8")
    fig_fan.update_layout(**chart_layout("Price Fan: Forecast vs Horizon (trading days)", 360))
    fig_fan.update_xaxes(title_text="Forecast Horizon (trading days)")
    fig_fan.update_yaxes(title_text="Price (USD)")
    st.plotly_chart(fig_fan, use_container_width=True)

    # Rolling VaR over time
    rv_series = log_returns(prices).rolling(63).apply(
        lambda x: np.percentile(x, (1-conf_pct/100)*100), raw=True
    ) * 100
    fig_rv2 = go.Figure()
    fig_rv2.add_trace(go.Scatter(
        x=rv_series.index, y=rv_series, name=f"Rolling VaR {conf_pct}% (63d)",
        line=dict(color="#f59e0b",width=1.5),
        fill="tozeroy", fillcolor="rgba(245,158,11,.07)",
    ))
    fig_rv2.update_layout(**chart_layout(f"Rolling Historical VaR {conf_pct}% (%)", 280))
    st.plotly_chart(fig_rv2, use_container_width=True)

    horizons = horizon_targets
    var_vals = [horizon_stats[h]["var"] * 100 for h in horizons]
    cvar_vals = [horizon_stats[h]["cvar"] * 100 for h in horizons]
    prob_vals = [horizon_stats[h]["prob_profit"] for h in horizons]
    std_vals = [horizon_stats[h]["std"] for h in horizons]
    spread_vals = [horizon_stats[h]["spread"] for h in horizons]
    spread_pct_vals = [horizon_stats[h]["spread_pct"] for h in horizons]
    tail_probs = [horizon_stats[h]["tail_prob"] for h in horizons]
    ratio_vals = [horizon_stats[h]["ratio"] for h in horizons]

    fig_risk_grid = make_subplots(
        rows=4, cols=2,
        subplot_titles=[
            "VaR (%) vs Horizon", "CVaR (%) vs Horizon",
            "Profit Probability (%)", "Std Dev vs Horizon",
            "P95-P5 Width (USD)", "P95-P5 Width (%)",
            "Tail Risk: ≤90% Price", "P95 / Current Price Ratio",
        ],
        vertical_spacing=0.06, horizontal_spacing=0.05,
    )
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=var_vals, line=dict(color="#f59e0b", width=1.5), mode="lines+markers",
    ), row=1, col=1)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=cvar_vals, line=dict(color="#f06060", width=1.5), mode="lines+markers",
    ), row=1, col=2)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=prob_vals, line=dict(color="#22d3b0", width=1.5),
    ), row=2, col=1)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=std_vals, line=dict(color="#7c83f5", width=1.5),
    ), row=2, col=2)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=spread_vals, line=dict(color="#fb923c", width=1.5),
    ), row=3, col=1)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=spread_pct_vals, line=dict(color="#6ee7d0", width=1.5),
    ), row=3, col=2)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=tail_probs, line=dict(color="#f06060", width=1.5),
    ), row=4, col=1)
    fig_risk_grid.add_trace(go.Scatter(
        x=horizons, y=ratio_vals, line=dict(color="#22d3b0", width=1.5),
    ), row=4, col=2)
    fig_risk_grid.update_layout(**grid_layout(f"{ticker} · Risk Micro Metrics", height=1120))
    st.plotly_chart(fig_risk_grid, use_container_width=True)


# ─────────────── TAB 5 · STATISTICS ─────────────────────────────
with tab_stats:
    c1, c2 = st.columns(2)
    with c1:
        lr = log_ret * 100
        x_n = np.linspace(float(lr.min()), float(lr.max()), 200)
        norm_y = (1/(float(lr.std())*np.sqrt(2*np.pi))) * \
                 np.exp(-0.5*((x_n-float(lr.mean()))/float(lr.std()))**2)
        fig_lr = go.Figure()
        fig_lr.add_trace(go.Histogram(x=lr, nbinsx=80, histnorm="probability density",
                                      marker_color="#7c83f5", opacity=.75, name="Empirical"))
        fig_lr.add_trace(go.Scatter(x=x_n, y=norm_y, name="Normal fit",
                                    line=dict(color="#f59e0b",width=2,dash="dash")))
        fig_lr.update_layout(**chart_layout("Log-Return Distribution vs Normal", 320))
        st.plotly_chart(fig_lr, use_container_width=True)

    with c2:
        sl = np.sort(lr)
        n  = len(sl)
        probs = np.arange(1,n+1)/(n+1)
        nq    = np.quantile(np.random.normal(float(lr.mean()),float(lr.std()),50000), probs)
        fig_qq = go.Figure()
        fig_qq.add_trace(go.Scatter(x=nq, y=sl, mode="markers",
                                    marker=dict(color="#7c83f5",size=3,opacity=.5), name="Q-Q"))
        mn = min(float(nq.min()),float(sl.min())); mx = max(float(nq.max()),float(sl.max()))
        fig_qq.add_trace(go.Scatter(x=[mn,mx],y=[mn,mx],
                                    line=dict(color="#f06060",dash="dash"),name="Normal"))
        fig_qq.update_layout(**chart_layout("Q-Q Plot (vs Normal)", 320))
        st.plotly_chart(fig_qq, use_container_width=True)

    # ACF
    max_lag = min(40, len(lr)//4)
    acf_v   = [float(lr.autocorr(lag=k)) for k in range(1, max_lag+1)]
    ci      = 1.96/np.sqrt(len(lr))
    fig_acf = go.Figure()
    fig_acf.add_trace(go.Bar(
        x=list(range(1,max_lag+1)), y=acf_v,
        marker_color=["#22d3b0" if abs(v)>ci else "#4b5675" for v in acf_v],
    ))
    fig_acf.add_hline(y=ci,  line_dash="dash",line_color="#f59e0b",annotation_text="+95% CI")
    fig_acf.add_hline(y=-ci, line_dash="dash",line_color="#f59e0b",annotation_text="-95% CI")
    fig_acf.update_layout(**chart_layout("Autocorrelation of Daily Returns (ACF)", 300))
    st.plotly_chart(fig_acf, use_container_width=True)

    # Stats table
    st.markdown("#### 📋 Full Quantitative Summary")
    stats_d = {
        "Last Price":            f"${last_price:.4f}",
        "Daily Change":          f"{daily_chg:+.3f}%",
        "YTD Return":            f"{ytd_ret:+.2f}%",
        "Annual Drift μ":        f"{mu_ann*100:.3f}%",
        "Annual Volatility σ":   f"{sigma_ann*100:.3f}%",
        "Daily Mean Return":     f"{mu_d*100:.4f}%",
        "Daily Std Dev":         f"{sigma_d*100:.4f}%",
        "Skewness":              f"{float(log_ret.skew()):.4f}",
        "Excess Kurtosis":       f"{float(log_ret.kurtosis()):.4f}",
        "Sharpe Ratio (rf=0)":   f"{sharpe:.4f}",
        "Max Drawdown":          f"{max_dd:.2f}%",
        f"VaR {conf_pct}%":      f"{var_*100:.3f}%",
        f"CVaR {conf_pct}%":     f"{cvar_*100:.3f}%",
        "MC Median Price":       f"${med_p:.4f}",
        "MC Mean Price":         f"${mean_p:.4f}",
        "MC P5 Price":           f"${p5:.4f}",
        "MC P95 Price":          f"${p95:.4f}",
        "P(Profit)":             f"{prob_prof:.2f}%",
        "Data Points":           f"{len(prices):,}",
        "Simulations":           f"{n_simulations:,}",
    }
    items = list(stats_d.items()); half = len(items)//2
    sc1, sc2 = st.columns(2)
    for col_x, chunk in [(sc1, items[:half]), (sc2, items[half:])]:
        rows_html = "".join(
            f"<tr><td style='color:#4b5675'>{k}</td>"
            f"<td style='color:#dde1f0;text-align:right'><b>{v}</b></td></tr>"
            for k, v in chunk
        )
        col_x.markdown(
            f'<table class="styled-table"><thead>'
            f'<tr><th>Metric</th><th style="text-align:right">Value</th></tr>'
            f'</thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True,
        )

    return_ecdf_x = np.sort(lr)
    return_ecdf_y = np.arange(1, len(lr) + 1) / len(lr)
    mu_lr = float(lr.mean())
    sigma_lr = float(lr.std())
    norm_ecdf = 0.5 * (1 + np.array([
        math.erf((val - mu_lr) / (sigma_lr * np.sqrt(2))) if sigma_lr > 0 else 0
        for val in return_ecdf_x
    ]))
    rolling_mean_21 = lr.rolling(21).mean()
    rolling_std_21 = lr.rolling(21).std()
    cum_pos = (lr > 0).cumsum()
    cum_neg = (lr < 0).cumsum()
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    violin_values = {
        label: lr[lr.index.weekday == idx]
        for idx, label in enumerate(weekday_names)
    }
    return_vs_volume = None
    if volumes is not None:
        return_vs_volume = pd.DataFrame({
            "return": lr,
            "volume": volumes.reindex(lr.index),
        }).dropna()

    fig_stats_grid = make_subplots(
        rows=4, cols=2,
        subplot_titles=[
            "Empirical CDF vs Normal", "Moment Snapshot",
            "Rolling Mean (21d)", "Rolling Std Dev (21d)",
            "Cumulative + / - Days", "Cumulative Smoothed",
            "Weekday Return Bands", "Return vs Volume",
        ],
        vertical_spacing=0.06, horizontal_spacing=0.05,
    )
    fig_stats_grid.add_trace(go.Scatter(
        x=return_ecdf_x, y=return_ecdf_y,
        line=dict(color="#22d3b0", width=2), name="Empirical CDF"
    ), row=1, col=1)
    fig_stats_grid.add_trace(go.Scatter(
        x=return_ecdf_x, y=norm_ecdf,
        line=dict(color="#fbbf24", width=1.5, dash="dash"), name="Normal"
    ), row=1, col=1)
    moments = {
        "Mean": mu_lr,
        "Std": sigma_lr,
        "Skew": float(log_ret.skew()),
        "Kurt": float(log_ret.kurtosis()),
    }
    fig_stats_grid.add_trace(go.Bar(
        x=list(moments.keys()), y=list(moments.values()),
        marker_color=["#22d3b0", "#fb923c", "#f06060", "#7c83f5"],
    ), row=1, col=2)
    fig_stats_grid.add_trace(go.Scatter(
        x=rolling_mean_21.index, y=rolling_mean_21,
        line=dict(color="#7c83f5", width=1.5),
    ), row=2, col=1)
    fig_stats_grid.add_trace(go.Scatter(
        x=rolling_std_21.index, y=rolling_std_21,
        line=dict(color="#fbbf24", width=1.5),
    ), row=2, col=2)
    fig_stats_grid.add_trace(go.Scatter(
        x=cum_pos.index, y=cum_pos, line=dict(color="#22d3b0", width=1.5),
        name="Positive Days"
    ), row=3, col=1)
    fig_stats_grid.add_trace(go.Scatter(
        x=cum_neg.index, y=cum_neg, line=dict(color="#f06060", width=1.5),
        name="Negative Days"
    ), row=3, col=1)
    for label, values in violin_values.items():
        if not values.empty:
            fig_stats_grid.add_trace(go.Violin(
                x=[label] * len(values), y=values,
                name=label, spanmode="hard", line=dict(width=1),
                marker=dict(color="#7c83f5"), points=False
            ), row=4, col=1)
    if return_vs_volume is not None and not return_vs_volume.empty:
        fig_stats_grid.add_trace(go.Scatter(
            x=return_vs_volume["return"], y=return_vs_volume["volume"],
            mode="markers", marker=dict(color="#22d3b0", size=4, opacity=0.5),
        ), row=4, col=2)
    fig_stats_grid.update_layout(**grid_layout(f"{ticker} · Statistics Micro Metrics", height=1120))
    st.plotly_chart(fig_stats_grid, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# AUTO-REFRESH TIMER
# ════════════════════════════════════════════════════════════════════
if continuous_mode:
    elapsed   = time.time() - st.session_state.last_fetch
    remaining = max(0, refresh_secs - elapsed)
    prog_val  = 1 - (remaining / refresh_secs)

    st.markdown("---")
    pc1, pc2 = st.columns([3,1])
    pc1.progress(
        min(prog_val, 1.0),
        text=f"⏱ Next auto-refresh in **{int(remaining)}s**  ·  interval: {refresh_secs}s",
    )
    pc2.markdown(
        f'<div style="color:#4b5675;font-size:11px;font-family:JetBrains Mono,monospace;'
        f'text-align:right">Refreshes: {st.session_state.refresh_counter}</div>',
        unsafe_allow_html=True,
    )
    time.sleep(min(5, max(1, remaining)))
    st.rerun()

# ════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<hr style="border-color:#161829;margin-top:40px">
<div style="color:#2e3350;font-size:11px;font-family:JetBrains Mono,monospace;
            text-align:center;padding:10px 0 20px">
⚠️ BUILT BY SOURISH DEY  · NOT FINANCIAL ADVICE ·
DATA: YAHOO FINANCE  · MODEL: GEOMETRIC BROWNIAN MOTION (GBM)
</div>
""", unsafe_allow_html=True)
