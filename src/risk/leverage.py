"""Paper-trading leverage scenario calculations."""
from __future__ import annotations


def leverage_plan(side: str, entry: float, leverage: float, stop_pct: float, target_pct: float, capital: float) -> dict[str, float]:
    side = side.upper()
    if side not in {"LONG", "SHORT"}:
        raise ValueError("Position must be LONG or SHORT")
    if entry <= 0 or leverage <= 0 or capital <= 0 or stop_pct <= 0 or target_pct <= 0:
        raise ValueError("Entry, leverage, percentages and capital must be positive")
    notional = capital * leverage
    units = notional / entry
    stop = entry * (1 - stop_pct / 100) if side == "LONG" else entry * (1 + stop_pct / 100)
    target = entry * (1 + target_pct / 100) if side == "LONG" else entry * (1 - target_pct / 100)
    max_loss = capital * leverage * stop_pct / 100
    potential_profit = capital * leverage * target_pct / 100
    return {
        "notional": notional, "units": units, "stop": stop, "target": target,
        "max_loss": max_loss, "potential_profit": potential_profit,
        "reward_risk": target_pct / stop_pct,
    }
