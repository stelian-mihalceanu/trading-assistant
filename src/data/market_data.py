"""Market-data retrieval helpers for the educational trading assistant."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

VALID_PERIODS = ("1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max")


def normalize_ticker(ticker: str) -> str:
    """Normalize a ticker symbol entered by a user."""
    normalized = ticker.strip().upper()
    if not normalized:
        raise ValueError("Ticker symbol cannot be empty.")
    return normalized


def get_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Return historical OHLCV data for a ticker.

    The returned data is for analysis only and may be delayed, adjusted, or incomplete.
    """
    symbol = normalize_ticker(ticker)
    if period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period}")

    data = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)

    if data.empty:
        raise ValueError(
            f"No market data was returned for '{symbol}'. Check the ticker and try again."
        )

    data = data.reset_index()
    date_column = "Datetime" if "Datetime" in data.columns else "Date"
    data = data.rename(columns={date_column: "Date"})
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)

    required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing expected market-data columns: {missing}")

    return data[required_columns].dropna().reset_index(drop=True)


def get_latest_quote(data: pd.DataFrame) -> dict[str, float]:
    """Create a small latest-price summary from historical data."""
    if data.empty:
        raise ValueError("Cannot calculate a quote from an empty DataFrame.")

    latest_close = float(data["Close"].iloc[-1])
    previous_close = float(data["Close"].iloc[-2]) if len(data) > 1 else latest_close
    change_percent = ((latest_close - previous_close) / previous_close * 100) if previous_close else 0.0

    return {
        "latest_close": latest_close,
        "previous_close": previous_close,
        "change_percent": change_percent,
    }
