"""Technical-indicator calculations used by the trading assistant."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_ohlcv(data: pd.DataFrame) -> None:
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of OHLCV data enriched with common technical indicators."""
    _validate_ohlcv(data)
    df = data.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    df["SMA_20"] = close.rolling(window=20, min_periods=20).mean()
    df["SMA_50"] = close.rolling(window=50, min_periods=50).mean()
    df["SMA_200"] = close.rolling(window=200, min_periods=200).mean()
    df["EMA_20"] = close.ewm(span=20, adjust=False, min_periods=20).mean()

    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    average_loss = losses.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + relative_strength))

    ema_12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema_26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False, min_periods=9).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    rolling_std = close.rolling(window=20, min_periods=20).std()
    df["BB_MIDDLE"] = df["SMA_20"]
    df["BB_UPPER"] = df["BB_MIDDLE"] + 2 * rolling_std
    df["BB_LOWER"] = df["BB_MIDDLE"] - 2 * rolling_std

    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["ATR_14"] = true_range.rolling(window=14, min_periods=14).mean()

    df["VOLUME_SMA_20"] = df["Volume"].rolling(window=20, min_periods=20).mean()
    df["RELATIVE_VOLUME"] = df["Volume"] / df["VOLUME_SMA_20"].replace(0, np.nan)

    return df


def latest_indicator_values(data: pd.DataFrame) -> dict[str, float]:
    """Return the latest non-null indicator values needed by the signal engine."""
    required = ["Close", "SMA_20", "SMA_50", "SMA_200", "RSI_14", "MACD", "MACD_SIGNAL", "ATR_14", "RELATIVE_VOLUME"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Indicator columns are missing: {missing}")

    latest = data.iloc[-1]
    return {
        key.lower(): float(latest[key]) if pd.notna(latest[key]) else float("nan")
        for key in required
    }
