import pandas as pd
import numpy as np
from src.backtest.simple_backtest import SimpleBacktest


def test_simple_backtest_basic():
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "close": np.arange(100, 160, dtype=float),
    })

    signals = pd.DataFrame({
        "timestamp": [dates[10], dates[30], dates[50]],
        "signal": ["BUY", "SELL", "BUY"],
        "indicator": ["TEST"] * 3,
        "value": [1.0] * 3,
        "price": [110.0, 130.0, 150.0],
    })

    bt = SimpleBacktest(df, signals, initial_capital=10000)
    trades = bt.run()

    assert isinstance(trades, pd.DataFrame)
    if not trades.empty:
        assert {"entry_time", "exit_time", "entry_price", "exit_price", "pnl", "type"}.issubset(trades.columns)
