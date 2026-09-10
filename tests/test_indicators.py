import numpy as np
import pandas as pd

from src.indicators.technical import add_technical_indicators


def make_ohlcv(rows: int = 250) -> pd.DataFrame:
    close = np.linspace(100, 150, rows)
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "Open": close - 0.5,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": np.full(rows, 1_000_000),
        }
    )


def test_add_technical_indicators_adds_expected_columns():
    result = add_technical_indicators(make_ohlcv())

    expected = {"SMA_20", "SMA_50", "SMA_200", "EMA_20", "RSI_14", "MACD", "MACD_SIGNAL", "ATR_14", "RELATIVE_VOLUME"}
    assert expected.issubset(result.columns)
    assert not pd.isna(result["SMA_200"].iloc[-1])
    assert not pd.isna(result["ATR_14"].iloc[-1])
