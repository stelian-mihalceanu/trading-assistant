from src.data.catalog import EXCHANGES, POPULAR_TICKERS
from src.ml.composite import composite_ai_score
from src.risk.leverage import leverage_plan


def test_exchange_catalog_contains_requested_markets():
    assert set(EXCHANGES) == {"NYSE", "LSE", "GERMANY", "SPAIN", "FRANCE"}
    assert "CRWD" in POPULAR_TICKERS["NYSE"].values()


def test_composite_score_is_bounded():
    result = composite_ai_score(
        {"rsi_14": 45.0, "macd": 2.0, "macd_signal": 1.0},
        {"profit_margin": 0.2, "roe": 0.15, "revenue_growth": 0.1},
        {"consensus_score": 0.5},
    )
    assert 0 <= result["score"] <= 100
    assert result["label"] in {"Strong", "Positive", "Neutral", "Cautious", "Weak"}


def test_long_and_short_leverage_targets():
    long_plan = leverage_plan("LONG", 100, 3, 5, 10, 1000)
    short_plan = leverage_plan("SHORT", 100, 3, 5, 10, 1000)
    assert long_plan["stop"] == 95
    assert long_plan["target"] == 110
    assert short_plan["stop"] == 105
    assert short_plan["target"] == 90
    assert long_plan["reward_risk"] == 2
