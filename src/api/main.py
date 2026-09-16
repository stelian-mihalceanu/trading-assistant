from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.data.market_data import get_latest_quote, get_price_history, normalize_ticker
from src.indicators.technical import add_technical_indicators, latest_indicator_values
from src.risk.position_sizing import calculate_position_size
from src.signals.signal_engine import build_signal

app = FastAPI(title="Trading Assistant API", version="1.0.0")


class AnalysisResponse(BaseModel):
    ticker: str
    timestamp: datetime
    price: float
    change_percent: float
    indicators: dict[str, Optional[float]]
    signal: dict
    position_size: Optional[int] = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analysis/{ticker}", response_model=AnalysisResponse)
def get_analysis(
    ticker: str,
    period: str = Query("1y", pattern="^(1mo|3mo|6mo|1y|2y|5y|10y|max)$"),
    account_balance: Optional[float] = Query(None, gt=0),
    risk_percent: float = Query(1.0, gt=0, le=100),
):
    try:
        symbol = normalize_ticker(ticker)
        prices = get_price_history(symbol, period=period)
        analyzed = add_technical_indicators(prices)
        quote = get_latest_quote(analyzed)
        indicators = latest_indicator_values(analyzed)
        signal = build_signal(indicators)

        position_size = None
        if account_balance and indicators.get("atr_14") == indicators.get("atr_14"):
            stop = quote["latest_close"] - (indicators["atr_14"] * 1.5)
            if stop > 0:
                position_size = calculate_position_size(
                    account_value=account_balance,
                    risk_percent=risk_percent,
                    entry_price=quote["latest_close"],
                    stop_price=stop,
                )

        return AnalysisResponse(
            ticker=symbol,
            timestamp=datetime.now(timezone.utc),
            price=quote["latest_close"],
            change_percent=quote["change_percent"],
            indicators={
                "sma_20": indicators.get("sma_20"),
                "sma_50": indicators.get("sma_50"),
                "sma_200": indicators.get("sma_200"),
                "rsi_14": indicators.get("rsi_14"),
                "macd": indicators.get("macd"),
                "macd_signal": indicators.get("macd_signal"),
                "atr_14": indicators.get("atr_14"),
                "atr_percent": indicators.get("atr_percent"),
            },
            signal={
                "label": signal.label,
                "score": signal.score,
                "reasons": signal.reasons,
                "risk_notes": signal.risk_notes,
            },
            position_size=position_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Market analysis failed") from exc
