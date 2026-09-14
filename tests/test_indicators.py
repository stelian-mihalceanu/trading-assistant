import numpy as np
import pandas as pd
import pytest

from src.indicators.technical import add_technical_indicators, latest_indicator_values


def make_ohlcv(periods: int = 260) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=periods, freq="D")
    close = pd.Series(100 + np.arange(periods, dtype=float))
    return pd.DataFrame({
        "Date": dates,
        "Open": close - 0.5,
        "High": close + 1.0,
        "Low": close - 1.0,
        "Close": close,
        "Volume": np.full(periods, 1_000_000.0),
    })


def test_sma_and_ema_are_calculated():
    df = make_ohlcv()
    result = add_technical_indicators(df)
    assert result["SMA_20"].iloc[19] == pytest.approx(df["Close"].iloc[:20].mean())
    assert result["SMA_50"].iloc[49] == pytest.approx(df["Close"].iloc[:50].mean())
    assert result["SMA_200"].iloc[199] == pytest.approx(df["Close"].iloc[:200].mean())
    assert result["EMA_20"].notna().sum() > 0


def test_rsi_is_bounded_and_handles_monotonic_series():
    result = add_technical_indicators(make_ohlcv())
    assert result["RSI_14"].dropna().between(0, 100).all()
    assert result["RSI_14"].iloc[-1] == pytest.approx(100.0)


def test_atr_and_relative_volume_are_available():
    result = add_technical_indicators(make_ohlcv())
    assert result["ATR_14"].iloc[-1] > 0
    assert result["RELATIVE_VOLUME"].iloc[-1] == pytest.approx(1.0)
    assert result["ATR_PERCENT"].iloc[-1] > 0


def test_latest_indicator_values_exposes_required_fields():
    result = add_technical_indicators(make_ohlcv())
    latest = latest_indicator_values(result)
    assert {"close", "rsi_14", "atr_14", "atr_percent", "relative_volume"}.issubset(latest)
