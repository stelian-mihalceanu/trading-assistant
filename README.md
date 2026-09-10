# Trading Assistant

An educational market-analysis and paper-trading assistant built with Python.

> **Disclaimer:** This project is for educational and informational purposes only. It does not provide financial, investment, legal, or tax advice. Market data may be delayed or incomplete. Do not use this project as the sole basis for an investment decision.

## Features

- Download historical market data through `yfinance`.
- Interactive Streamlit dashboard.
- Candlestick chart with volume and technical-indicator overlays.
- SMA, EMA, RSI, MACD, Bollinger Bands, ATR, and relative-volume calculations.
- Explainable market-analysis signals: `BULLISH`, `NEUTRAL`, or `BEARISH`.
- Risk and position-size reference calculations for educational paper-trading scenarios.
- Unit tests for indicator and signal logic.

## First MVP Scope

1. Enter a ticker symbol such as `AAPL`, `MSFT`, `NVDA`, `SPY`, or `BTC-USD`.
2. Download historical OHLCV data.
3. Calculate technical indicators.
4. Inspect the chart and an explainable analysis summary.
5. Review volatility-based educational risk references.

No brokerage execution, real-money orders, or investment recommendations are included.

## Tech Stack

- Python 3.11+
- Streamlit
- yfinance
- pandas and numpy
- Plotly
- pytest
- Ruff

## Project Structure

```text
trading-assistant/
├── app/
│   └── streamlit_app.py
├── src/
│   ├── data/
│   │   └── market_data.py
│   ├── indicators/
│   │   └── technical.py
│   ├── signals/
│   │   └── signal_engine.py
│   └── risk/
│       └── position_sizing.py
├── tests/
├── requirements.txt
├── .env.example
└── .gitignore
```

## Local Setup

```bash
git clone https://github.com/stelian-mihalceanu/trading-assistant.git
cd trading-assistant

conda create -n trading-assistant python=3.11 -y
conda activate trading-assistant
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app/streamlit_app.py
```

## Tests

```bash
pytest
```

## Example Workflow

Open the dashboard, select `SPY`, choose a one-year history period, and inspect the trend, RSI, MACD, ATR, and explanatory signal reasons. Treat the result as analysis—not a recommendation to buy or sell.
