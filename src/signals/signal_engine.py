"""Explainable market-analysis signal logic.

Signals are informational summaries, not investment recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import math


@dataclass(frozen=True)
class AnalysisSignal:
    """An explainable market-analysis result."""

    label: str
    score: int
    reasons: list[str]
    risk_notes: list[str]


def _is_number(value: float) -> bool:
    return value is not None and not math.isnan(float(value))


def build_signal(indicators: Mapping[str, float]) -> AnalysisSignal:
    """Create BULLISH, NEUTRAL, or BEARISH analysis from latest indicators."""
    required = ["close", "sma_20", "sma_50", "sma_200", "rsi_14", "macd", "macd_signal", "atr_14", "relative_volume"]
    missing = [key for key in required if key not in indicators or not _is_number(indicators[key])]
    if missing:
        return AnalysisSignal(
            label="INSUFFICIENT_DATA",
            score=0,
            reasons=["More price history is required before the full indicator set can be evaluated."],
            risk_notes=["Use at least 200 daily observations for the SMA 200 trend reference."],
        )

    close = float(indicators["close"])
    sma_20 = float(indicators["sma_20"])
    sma_50 = float(indicators["sma_50"])
    sma_200 = float(indicators["sma_200"])
    rsi = float(indicators["rsi_14"])
    macd = float(indicators["macd"])
    macd_signal = float(indicators["macd_signal"])
    atr = float(indicators["atr_14"])
    relative_volume = float(indicators["relative_volume"])

    score = 0
    reasons: list[str] = []
    risk_notes: list[str] = []

    if close > sma_50:
        score += 1
        reasons.append("Price is above the SMA 50 trend reference.")
    else:
        score -= 1
        reasons.append("Price is below the SMA 50 trend reference.")

    if close > sma_200:
        score += 1
        reasons.append("Price is above the SMA 200 long-term trend reference.")
    else:
        score -= 1
        reasons.append("Price is below the SMA 200 long-term trend reference.")

    if sma_50 > sma_200:
        score += 1
        reasons.append("SMA 50 is above SMA 200, which supports the long-term trend.")
    else:
        score -= 1
        reasons.append("SMA 50 is below SMA 200, which weakens the long-term trend.")

    if macd > macd_signal:
        score += 1
        reasons.append("MACD is above its signal line.")
    else:
        score -= 1
        reasons.append("MACD is below its signal line.")

    if 45 <= rsi <= 65:
        score += 1
        reasons.append(f"RSI is {rsi:.1f}, indicating neutral-to-positive momentum without an extreme reading.")
    elif rsi > 70:
        score -= 1
        reasons.append(f"RSI is {rsi:.1f}; momentum is elevated and may be overextended.")
        risk_notes.append("Elevated RSI can increase pullback risk; avoid treating momentum as certainty.")
    elif rsi < 30:
        score += 1
        reasons.append(f"RSI is {rsi:.1f}; the asset is in an oversold zone, which can be volatile.")
        risk_notes.append("An oversold RSI is not a guarantee of a reversal.")
    else:
        reasons.append(f"RSI is {rsi:.1f}, indicating mixed momentum.")

    if relative_volume >= 1.2:
        score += 1
        reasons.append(f"Relative volume is {relative_volume:.2f}x the 20-day average.")
    elif relative_volume < 0.7:
        reasons.append(f"Relative volume is only {relative_volume:.2f}x the 20-day average.")

    atr_percent = (atr / close * 100) if close else 0.0
    risk_notes.append(f"ATR is {atr:.2f} ({atr_percent:.2f}% of the current price), a reference for recent daily volatility.")
    risk_notes.append("This signal is educational analysis only and is not a buy, sell, or hold recommendation.")

    if score >= 3:
        label = "BULLISH"
    elif score <= -2:
        label = "BEARISH"
    else:
        label = "NEUTRAL"

    return AnalysisSignal(label=label, score=score, reasons=reasons, risk_notes=risk_notes)
