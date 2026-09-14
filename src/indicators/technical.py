"""Technical-indicator calculations used by the trading assistant."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_ohlcv(data: pd.DataFrame) -> None:
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")


def _wilder_mean(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Return OHLCV data enriched with common technical indicators."""
    _validate_ohlcv(data)
    df = data.copy()
    close = pd.to_numeric(df["Close"], errors="coerce")
    high = pd.to_numeric(df["High"], errors="coerce")
    low = pd.to_numeric(df["Low"], errors="coerce")
    volume = pd.to_numeric(df["Volume"], errors="coerce")

    df["SMA_20"] = close.rolling(20, min_periods=20).mean()
    df["SMA_50"] = close.rolling(50, min_periods=50).mean()
    df["SMA_200"] = close.rolling(200, min_periods=200).mean()
    df["EMA_20"] = close.ewm(span=20, adjust=False, min_periods=20).mean()

    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = _wilder_mean(gains, 14)
    average_loss = _wilder_mean(losses, 14)
    rs = average_gain / average_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.mask(average_loss.eq(0) & average_gain.gt(0), 100.0)
    rsi = rsi.mask(average_gain.eq(0) & average_loss.gt(0), 0.0)
    rsi = rsi.mask(average_gain.eq(0) & average_loss.eq(0), 50.0)
    df["RSI_14"] = rsi

    ema_12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema_26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False, min_periods=9).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    rolling_std = close.rolling(20, min_periods=20).std()
    df["BB_MIDDLE"] = df["SMA_20"]
    df["BB_UPPER"] = df["BB_MIDDLE"] + 2 * rolling_std
    df["BB_LOWER"] = df["BB_MIDDLE"] - 2 * rolling_std

    previous_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    ).max(axis=1)
    df["TRANGE"] = true_range
    df["ATR_14"] = _wilder_mean(true_range, 14)
    df["VOLUME_SMA_20"] = volume.rolling(20, min_periods=20).mean()
    df["RELATIVE_VOLUME"] = volume / df["VOLUME_SMA_20"].replace(0, np.nan)
    df["ATR_PERCENT"] = (df["ATR_14"] / close.replace(0, np.nan)) * 100
    return df


def latest_indicator_values(data: pd.DataFrame) -> dict[str, float]:
    """Return the latest indicator values needed by the signal engine."""
    required = [
        "Close", "SMA_20", "SMA_50", "SMA_200", "RSI_14", "MACD",
        "MACD_SIGNAL", "ATR_14", "RELATIVE_VOLUME", "ATR_PERCENT",
    ]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Indicator columns are missing: {missing}")
    latest = data.iloc[-1]
    return {key.lower(): float(latest[key]) if pd.notna(latest[key]) else float("nan") for key in required}
