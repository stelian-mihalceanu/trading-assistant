from src.signals.signal_engine import build_signal


def test_bullish_signal_for_consistent_positive_indicators():
    indicators = {
        "close": 120.0,
        "sma_20": 115.0,
        "sma_50": 110.0,
        "sma_200": 100.0,
        "rsi_14": 55.0,
        "macd": 2.0,
        "macd_signal": 1.0,
        "atr_14": 3.0,
        "relative_volume": 1.3,
    }

    result = build_signal(indicators)

    assert result.label == "BULLISH"
    assert result.score >= 3
    assert result.reasons


def test_insufficient_data_signal_when_values_are_missing():
    indicators = {
        "close": 120.0,
        "sma_20": float("nan"),
        "sma_50": 110.0,
        "sma_200": 100.0,
        "rsi_14": 55.0,
        "macd": 2.0,
        "macd_signal": 1.0,
        "atr_14": 3.0,
        "relative_volume": 1.3,
    }

    result = build_signal(indicators)

    assert result.label == "INSUFFICIENT_DATA"
