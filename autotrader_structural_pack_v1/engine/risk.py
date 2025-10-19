from __future__ import annotations
def position_size(balance_usd: float, risk_pct: float, atr: float, atr_multiple: float = 1.5) -> float:
    if atr <= 0: return 0.0
    risk_usd = balance_usd * risk_pct
    return max(0.0, risk_usd / (atr * atr_multiple))
