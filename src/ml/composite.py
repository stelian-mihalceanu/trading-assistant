"""Transparent multi-factor research score.

This is a ranking aid, not a forecast guarantee. It deliberately exposes the
components so users can see why a score moves.
"""
from __future__ import annotations


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def composite_ai_score(indicators: dict, company: dict, analyst: dict) -> dict:
    rsi = indicators.get("rsi_14")
    macd = indicators.get("macd")
    signal = indicators.get("macd_signal")
    technical = 50.0
    if rsi == rsi:
        technical += max(-20, min(20, (50 - rsi) * 0.45))
    if macd == macd and signal == signal:
        technical += 12 if macd > signal else -12
    fundamental = 50.0
    margin = company.get("profit_margin")
    roe = company.get("roe")
    growth = company.get("revenue_growth")
    if isinstance(margin, (int, float)):
        fundamental += max(-12, min(12, margin * 60))
    if isinstance(roe, (int, float)):
        fundamental += max(-12, min(12, roe * 30))
    if isinstance(growth, (int, float)):
        fundamental += max(-10, min(10, growth * 25))
    analyst_score = 50 + float(analyst.get("consensus_score", 0)) * 20
    score = _clip(0.45 * technical + 0.35 * fundamental + 0.20 * analyst_score)
    label = "Strong" if score >= 70 else "Positive" if score >= 55 else "Neutral" if score >= 45 else "Cautious" if score >= 30 else "Weak"
    return {"score": score, "label": label, "technical": technical, "fundamental": fundamental, "analyst": analyst_score}
