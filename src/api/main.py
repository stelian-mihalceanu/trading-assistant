from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.data.market_data import MarketData
from src.indicators.technical import TechnicalIndicators
from src.signals.signal_engine import SignalEngine
from src.risk.position_sizing import PositionSizing


app = FastAPI(
    title="Trading Assistant API",
    description="API pentru analiză tehnică, semnale și position sizing",
    version="0.2.0"
)


class SignalResponse(BaseModel):
    timestamp: datetime
    signal: str
    indicator: str
    value: float
    price: float


class AnalysisResponse(BaseModel):
    ticker: str
    start: str
    end: str
    indicators: dict
    signals: List[SignalResponse]
    position_size: Optional[dict] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "trading-assistant-api"}


@app.get("/analysis/{ticker}", response_model=AnalysisResponse)
def get_analysis(
    ticker: str,
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    account_balance: Optional[float] = Query(None, ge=0),
    risk_per_trade: Optional[float] = Query(0.01, ge=0, le=1),
):
    try:
        data = MarketData(ticker)
        df = data.get_historical_data(start=start, end=end)

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for ticker")

        indicators = TechnicalIndicators(df)
        df = indicators.add_sma(20).add_sma(50).add_rsi().add_macd()

        engine = SignalEngine(df)
        signals = engine.get_signals()

        response_signals = [
            SignalResponse(
                timestamp=row["timestamp"],
                signal=row["signal"],
                indicator=row["indicator"],
                value=row["value"],
                price=row["price"],
            )
            for _, row in signals.iterrows()
        ]

        position = None
        if account_balance and not signals.empty:
            last_row = df.iloc[-1]
            ps = PositionSizing(
                account_balance=account_balance,
                risk_per_trade=risk_per_trade,
                entry_price=last_row["close"],
                stop_loss_price=last_row["close"] * 0.95,
            )
            position = ps.calculate_position_size()

        return AnalysisResponse(
            ticker=ticker.upper(),
            start=start,
            end=end,
            indicators={
                "sma_20": float(df["sma_20"].iloc[-1]) if "sma_20" in df else None,
                "sma_50": float(df["sma_50"].iloc[-1]) if "sma_50" in df else None,
                "rsi": float(df["rsi"].iloc[-1]) if "rsi" in df else None,
            },
            signals=response_signals,
            position_size=position,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
