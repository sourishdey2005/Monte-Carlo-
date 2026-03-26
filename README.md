# Quantum Pulse Atlas — Monte Carlo Stock Simulator

**Description**  
Quantum Pulse Atlas is a Streamlit-powered Monte Carlo stock simulation dashboard that visualizes live and historical data alongside rich analytics. The app streams data from Yahoo Finance, runs GBM-based simulations, and surfaces more than 40 bespoke visual slices (including an 8-panel candlestick gallery and multiple microgrids per analysis tab) so you can explore price action, risk, technical, and statistical dimensions in one place.

## Features
1. **Live Data Refresh** – Continuous auto-refresh mode keeps the simulation updating until you pause it; refresh interval is configurable.
2. **Full Monte Carlo Suite** – Multiple projections (paths, distributions, percentiles, horizon stats) are rendered alongside profit/loss and return micro-metrics.
3. **Price & Volume Toolkit** – Candle/line charts, VWAP, volume metrics, weekday/month aggregates, and a dedicated gallery with daily, weekly, monthly, quarterly, and Heikin-Ashi candlestick views.
4. **Technical Intelligence** – RSI, MACD, Bollinger width, stochastic oscillators, rolling skew/kurtosis, Chaikin Money Flow, and EMA gap grids.
5. **Risk Dashboard** – VaR/CVaR across horizons, fan charts, scenario probabilities, rolling VaR, spread width, tail risk, and probability paths tracker.
6. **Statistical Explorer** – Log-return distributions vs. normal, ECDF, cumulative stats, violin plots, return vs. volume scatter, and detailed summary table.
7. **Custom Controls** – Pick from 120+ tickers, override μ/σ, adjust simulation parameters, and toggle chart components right from the sidebar.

## Prerequisites
- Python 3.10+ (tested in a 3.14 venv)
- `pip install -r requirements.txt` (See `Montec​​arlo/requirements.txt` for dependencies like Streamlit, Plotly, NumPy, pandas, yfinance.)

## Setup
1. Clone or copy the `Montecarlo` folder.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App
Launch Streamlit from the project root:
```bash
streamlit run stock_monte_carlo.py
```
The app configures the “Quantum Pulse Atlas” header, loads cached history, and immediately begins Monte Carlo runs once tickers are selected.

## Sidebar Controls
- **Stock selector**: Choose from 120+ curated tickers or enter any custom symbol (even crypto tickers like `BTC-USD`).
- **Historical window**: Pick a preset period or define a custom date range.
- **Simulation params**: Set the number of paths, horizon length (5–504 trading days), and confidence level for VaR.
- **Param override**: Manually specify annual drift (μ) and volatility (σ) if you want to test non-historical assumptions.
- **Live data**: Continuous simulation toggle, refresh interval selector, and manual refresh button.
- **Chart options**: Show/hide candlesticks, volume, Bollinger bands, SMA overlays, MACD, RSI, and Monte Carlo paths.

## Tab Overview
- **🎲 Monte Carlo**: Live MC paths, histograms, ECDFs, quantile ladder, return boxes, and above-today percentages.
- **📈 Price & Volume**: Candlestick gallery, VWAP overlay, range/volume grids, weekly/monthly stats, and VWAP vs. volume comparisons.
- **🔬 Technical**: RSI, MACD, Bollinger width, stochastic curves, volatility/skew/kurtosis trackers, Chaikin Money Flow, and EMA gap detection.
- **⚠️ Risk**: VaR/CVaR trends, scenario probabilities, fan charts, rolling VaR, horizon spread ratios, and tail risk.
- **📊 Statistics**: Log-return distribution, ECDF vs. normal curve, moment snapshots, rolling mean/std, cumulative day counts, weekday violins, and return-volume scatter.

## Data Flow & Performance Tips
- The app caches each tickers’ history and only refetches when the symbol/period changes or the refresh timer elapses.  
- Monte Carlo paths are recalculated on refresh; you can throttle the number of visible paths (`Visible MC Paths`) if the UI feels heavy.  
- Advanced microgrids reuse resampled OHLC slices to avoid repeated heavy calculations in each subplot.

## Notes
- All models are for educational/research use only; see the footer disclaimer in the UI.  
- The interface assumes trading days (GBM uses `dt=1/252`).  
- If you experience rate limits from Yahoo Finance, reducing the auto-refresh interval or disabling continuous mode will help.
