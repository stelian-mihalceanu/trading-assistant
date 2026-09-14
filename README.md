# Trading Assistant

An educational multi-market research and paper-trading assistant built with Python and Streamlit.

> **Disclaimer:** This project is for educational and informational purposes only. It does not provide financial, investment, legal, or tax advice. Market data may be delayed, incomplete, or unavailable. Do not use this project as the sole basis for an investment decision.

## Features

- Historical OHLCV data through `yfinance`, cached for 15 minutes.
- Interactive Streamlit research dashboard.
- Candlestick chart with SMA overlays.
- SMA, EMA, RSI, MACD, Bollinger Bands, ATR, true range and relative-volume calculations.
- Wilder-smoothed RSI and ATR handling for more standard technical calculations.
- Explainable `BULLISH`, `NEUTRAL`, `BEARISH` and `INSUFFICIENT_DATA` signals.
- Multi-factor research score from 0-100 with technical, fundamental, analyst, valuation and risk components.
- Confidence level and rule-based risk flags alongside the score.
- Cached company balance-sheet data.
- Educational leverage and position-size scenarios.
- Unit tests and GitHub Actions CI on Python 3.11.

## Research score

The score is a transparent ranking aid, not a prediction model. Components are exposed in the dashboard:

| Component | Purpose |
|---|---|
| Technical | Trend, momentum, moving averages, MACD and volume |
| Fundamental | Margins, ROE, growth, leverage and liquidity |
| Analyst | External analyst consensus |
| Valuation | P/E and forward P/E reference signals |
| Risk | Recent ATR-based volatility reference |

The dashboard also shows confidence and rule-based risk flags so a single headline score is not presented as certainty.

## Supported scope

1. Enter a ticker such as `AAPL`, `MSFT`, `NVDA`, `SPY`, or `BTC-USD`.
2. Download historical OHLCV data.
3. Calculate technical indicators.
4. Inspect the price chart and explainable signals.
5. Review company fundamentals and analyst consensus.
6. Review educational leverage/risk scenarios.

No brokerage execution, real-money orders, or investment recommendations are included.

## Tech Stack

- Python 3.11
- Streamlit
- yfinance
- pandas / numpy
- Plotly
- pytest
- Ruff

The project deliberately does **not** depend on `ta-lib`: the technical indicators are implemented directly with pandas/numpy, which keeps deployment simpler.

## Project Structure

```text
trading-assistant/
├── app/
│   └── streamlit_app.py
├── src/
│   ├── backtest/
│   ├── data/
│   ├── indicators/
│   ├── ml/
│   ├── risk/
│   └── signals/
├── tests/
├── .github/workflows/ci.yml
├── .python-version
├── requirements.txt
└── .streamlit/config.toml
```

## Local Setup

```bash
git clone https://github.com/stelian-mihalceanu/trading-assistant.git
cd trading-assistant

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app/streamlit_app.py
```

## Tests and lint

```bash
pytest -q
ruff check .
```

GitHub Actions runs both checks on Python 3.11 for pushes to `main`/upgrade branches and pull requests.

## Deployment

The application entrypoint is `app/streamlit_app.py`. Pin the Streamlit deployment runtime to Python 3.11 to match `.python-version` and CI. No system package for TA-Lib is required.

## Example Workflow

Open the dashboard, select `SPY`, choose a one-year history period, and inspect the trend, RSI, MACD, ATR, research-score components, analyst consensus and explanatory risk flags. Treat the result as analysis—not a recommendation to buy or sell.
