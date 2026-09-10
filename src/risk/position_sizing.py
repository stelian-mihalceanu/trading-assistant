"""Educational risk and position-size reference calculations."""

from __future__ import annotations


def calculate_risk_amount(account_value: float, risk_percent: float) -> float:
    """Calculate the maximum reference amount at risk for one paper trade."""
    if account_value <= 0:
        raise ValueError("Account value must be greater than zero.")
    if not 0 < risk_percent <= 100:
        raise ValueError("Risk percent must be greater than 0 and at most 100.")
    return account_value * (risk_percent / 100)


def calculate_position_size(account_value: float, risk_percent: float, entry_price: float, stop_price: float) -> int:
    """Calculate a whole-share reference position size for a paper-trading scenario."""
    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("Entry and stop prices must be greater than zero.")

    risk_per_share = abs(entry_price - stop_price)
    if risk_per_share == 0:
        raise ValueError("Entry price and stop price cannot be identical.")

    risk_amount = calculate_risk_amount(account_value, risk_percent)
    return int(risk_amount // risk_per_share)


def atr_stop_reference(entry_price: float, atr: float, atr_multiple: float = 1.5) -> float:
    """Return a simple long-position stop reference based on ATR; educational only."""
    if entry_price <= 0 or atr <= 0 or atr_multiple <= 0:
        raise ValueError("Entry price, ATR, and ATR multiple must be greater than zero.")
    return entry_price - atr * atr_multiple
