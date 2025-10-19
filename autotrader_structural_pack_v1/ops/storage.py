from __future__ import annotations
import json, os
from typing import List, Dict, Any
from sqlalchemy import select
from .db import get_session
from .models import Coin

def load_allowlist(path: str = "config/coins_allowlist.json") -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("universe", [])

def list_active_symbols() -> List[str]:
    with get_session() as s:
        rows = s.execute(select(Coin).where(Coin.active == True).order_by(Coin.symbol.asc()))
        return [r.Coin.symbol for r in rows]
