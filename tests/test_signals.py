import pandas as pd
import numpy as np
from src.signals.signal_engine import SignalEngine


def test_get_signals_basic():
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "close": np.arange(100, 160, dtype=float),
        "sma_20": np.arange(110, 170, dtype=float),
        "sma_50": np.arange(120, 180, dtype=float),
        "rsi": [50] * 60,
    })

    engine = SignalEngine(df)
    signals = engine.get_signals()

    assert isinstance(signals, pd.DataFrame)
    required_cols = {"timestamp", "signal", "indicator", "value", "price"}
    assert required_cols.issubset(signals.columns)


def test_confluence_signals():
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100))
    sma_20 = pd.Series(close).rolling(20).mean()
    sma_50 = pd.Series(close).rolling(50).mean()
    rsi = 50 + np.random.randn(100) * 5

    df = pd.DataFrame({
        "timestamp": dates,
        "close": close,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "rsi": rsi,
    })

    engine = SignalEngine(df)
    signals = engine.get_confluence_signals()

    assert isinstance(signals, pd.DataFrame)
    if not signals.empty:
        assert signals["signal"].isin(["BUY", "SELL"]).all()
