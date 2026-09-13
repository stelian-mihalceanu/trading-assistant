"""Company fundamentals and analyst data."""
from __future__ import annotations
from typing import Any
import pandas as pd
import yfinance as yf

def _num(value: Any):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

def get_company_snapshot(symbol: str) -> dict[str, Any]:
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.get_info()
    except Exception:
        info = {}
    return {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName") or symbol,
        "description": info.get("longBusinessSummary") or "Company description unavailable.",
        "sector": info.get("sector"), "industry": info.get("industry"), "country": info.get("country"),
        "website": info.get("website"), "market_cap": _num(info.get("marketCap")),
        "pe": _num(info.get("trailingPE")), "forward_pe": _num(info.get("forwardPE")),
        "peg": _num(info.get("pegRatio")), "price_to_book": _num(info.get("priceToBook")),
        "dividend_yield": _num(info.get("dividendYield")), "profit_margin": _num(info.get("profitMargins")),
        "operating_margin": _num(info.get("operatingMargins")), "roe": _num(info.get("returnOnEquity")),
        "revenue_growth": _num(info.get("revenueGrowth")), "earnings_growth": _num(info.get("earningsGrowth")),
        "debt_to_equity": _num(info.get("debtToEquity")), "current_ratio": _num(info.get("currentRatio")),
        "free_cash_flow": _num(info.get("freeCashflow")), "balance_sheet_date": None,
    }

def get_analyst_consensus(symbol: str) -> dict[str, Any]:
    ticker = yf.Ticker(symbol)
    counts = {"strong_buy": 0, "buy": 0, "hold": 0, "sell": 0, "strong_sell": 0}
    targets = {"low": None, "mean": None, "median": None, "high": None, "current": None}
    try:
        rec = ticker.recommendations
        if rec is not None and not rec.empty:
            row = rec.tail(1).iloc[0]
            mapping = {"strongBuy":"strong_buy", "buy":"buy", "hold":"hold", "sell":"sell", "strongSell":"strong_sell"}
            for source, dest in mapping.items():
                if source in row.index:
                    counts[dest] = int(_num(row[source]) or 0)
    except Exception:
        pass
    try:
        price_targets = ticker.analyst_price_targets
        if isinstance(price_targets, dict):
            for key in targets:
                targets[key] = _num(price_targets.get(key))
    except Exception:
        pass
    total = sum(counts.values())
    score = (counts["strong_buy"]*2 + counts["buy"] - counts["sell"] - counts["strong_sell"]*2) / total if total else 0.0
    return {"counts": counts, "total": total, "consensus_score": score, "label": "Bullish" if score > .35 else "Bearish" if score < -.35 else "Neutral", **targets}

def get_alpha_vantage_overview(symbol: str):
    return None
