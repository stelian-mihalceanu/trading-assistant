"""Transparent multi-factor research score.

The score is a ranking aid, not a forecast or investment recommendation.
Each component is normalized to 0-100 and exposed to the UI.
"""
from __future__ import annotations

import math


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _score_rsi(rsi: float) -> float:
    if not math.isfinite(rsi):
        return 50.0
    if rsi < 30:
        return 62.0
    if rsi < 45:
        return 55.0 + (rsi - 30) * 0.35
    if rsi <= 60:
        return 70.0 + (rsi - 45) * 1.0
    if rsi <= 70:
        return 85.0 - (rsi - 60) * 1.5
    return max(25.0, 70.0 - (rsi - 70) * 2.0)


def composite_ai_score(indicators: dict, company: dict, analyst: dict) -> dict:
    """Build a 0-100 multi-factor research score with confidence and risks."""
    close = indicators.get("close", float("nan"))
    sma20 = indicators.get("sma_20", float("nan"))
    sma50 = indicators.get("sma_50", float("nan"))
    sma200 = indicators.get("sma_200", float("nan"))
    rsi = indicators.get("rsi_14", float("nan"))
    macd = indicators.get("macd", float("nan"))
    macd_signal = indicators.get("macd_signal", float("nan"))
    relative_volume = indicators.get("relative_volume", float("nan"))
    atr_percent = indicators.get("atr_percent", float("nan"))

    technical = 50.0
    technical += 12 if all(math.isfinite(x) for x in (close, sma50)) and close > sma50 else -12
    technical += 10 if all(math.isfinite(x) for x in (close, sma200)) and close > sma200 else -10
    technical += 8 if all(math.isfinite(x) for x in (sma50, sma200)) and sma50 > sma200 else -8
    technical += 5 if all(math.isfinite(x) for x in (close, sma20)) and close > sma20 else -5
    technical += 12 if all(math.isfinite(x) for x in (macd, macd_signal)) and macd > macd_signal else -12
    technical = 0.65 * technical + 0.35 * _score_rsi(rsi)
    if math.isfinite(relative_volume):
        technical += _clip((relative_volume - 1.0) * 8, -8, 8)
    technical = _clip(technical)

    fundamental = 50.0
    margin = company.get("profit_margin")
    roe = company.get("roe")
    growth = company.get("revenue_growth")
    debt = company.get("debt_to_equity")
    current_ratio = company.get("current_ratio")
    for value, scale in ((margin, 55), (roe, 28), (growth, 25)):
        if isinstance(value, (int, float)) and math.isfinite(value):
            fundamental += _clip(value * scale, -15, 15)
    if isinstance(debt, (int, float)) and math.isfinite(debt):
        fundamental += _clip((1.5 - debt) * 6, -8, 8)
    if isinstance(current_ratio, (int, float)) and math.isfinite(current_ratio):
        fundamental += _clip((current_ratio - 1.0) * 5, -5, 5)
    fundamental = _clip(fundamental)

    consensus = float(analyst.get("consensus_score", 0) or 0)
    analyst_score = _clip(50 + consensus * 20)

    valuation = 50.0
    pe = company.get("pe")
    forward_pe = company.get("forward_pe")
    if isinstance(pe, (int, float)) and math.isfinite(pe) and pe > 0:
        valuation += _clip((25 - pe) * 0.7, -20, 20)
    if isinstance(forward_pe, (int, float)) and math.isfinite(forward_pe) and forward_pe > 0:
        valuation += _clip((22 - forward_pe) * 0.5, -15, 15)
    valuation = _clip(valuation)

    risk = 70.0
    if math.isfinite(atr_percent):
        risk = _clip(85 - atr_percent * 5, 15, 90)

    score = _clip(
        0.40 * technical
        + 0.25 * fundamental
        + 0.15 * analyst_score
        + 0.10 * valuation
        + 0.10 * risk
    )
    label = "Strong" if score >= 70 else "Positive" if score >= 55 else "Neutral" if score >= 45 else "Cautious" if score >= 30 else "Weak"

    spread = max(technical, fundamental, analyst_score, valuation, risk) - min(technical, fundamental, analyst_score, valuation, risk)
    confidence = "High" if spread < 25 else "Medium" if spread < 45 else "Low"

    risks: list[str] = []
    if math.isfinite(rsi) and rsi > 70:
        risks.append("RSI is elevated; momentum may be overextended.")
    if math.isfinite(atr_percent) and atr_percent > 4:
        risks.append("Daily ATR is elevated, implying higher recent volatility.")
    if isinstance(pe, (int, float)) and math.isfinite(pe) and pe > 35:
        risks.append("P/E is elevated relative to a generic valuation reference.")
    if technical < 45:
        risks.append("Technical trend/momentum factors are weakening.")
    if fundamental < 45:
        risks.append("Fundamental factors are mixed or weak.")
    if not risks:
        risks.append("No major rule-based risk flag was triggered.")

    return {
        "score": score,
        "label": label,
        "confidence": confidence,
        "technical": technical,
        "fundamental": fundamental,
        "analyst": analyst_score,
        "valuation": valuation,
        "risk": risk,
        "risks": risks,
    }
