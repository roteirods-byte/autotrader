from __future__ import annotations
import datetime as dt, pytz, os

def now_brt() -> dt.datetime:
    tz = pytz.timezone(os.getenv("TZ", "America/Sao_Paulo"))
    return dt.datetime.now(tz)
