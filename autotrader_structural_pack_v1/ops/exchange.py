from __future__ import annotations
import os, ccxt

def get_exchange():
    name = os.getenv("EXCHANGE", "binance")
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    secret = os.getenv("EXCHANGE_SECRET", "")
    klass = getattr(ccxt, name)
    ex = klass({
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
        "options": {"defaultType": "future"},
    })
    return ex
