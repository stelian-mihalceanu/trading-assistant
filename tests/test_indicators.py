import pandas as pd
import numpy as np
from src.indicators.technical import TechnicalIndicators


def test_add_sma():
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "close": np.arange(100, 160, dtype=float),
    })

    ind = TechnicalIndicators(df)
    result = ind.add_sma(20).df

    assert "sma_20" in result.columns
    assert result["sma_20"].iloc[19] == pytest.approx(df["close"].iloc[:20].mean())


def test_add_rsi():
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(60))

    df = pd.DataFrame({
        "timestamp": dates,
        "close": close,
    })

    ind = TechnicalIndicators(df)
    result = ind.add_rsi(period=14).df

    assert "rsi" in result.columns
    assert result["rsi"].dropna().between(0, 100).all()
