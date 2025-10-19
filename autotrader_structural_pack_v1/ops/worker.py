from __future__ import annotations
import os, time, datetime as dt
import pytz, structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from .storage import load_allowlist

log = structlog.get_logger()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def main():
    tz = pytz.timezone(os.getenv("TZ", "America/Sao_Paulo"))
    now = dt.datetime.now(tz)
    allow = load_allowlist()
    log.info("worker.start", now=str(now), allowlist=len(allow), app=os.getenv("APP_VERSION","v1"))
    # Observação: lógica de coleta/sinais será implementada após os painéis.
    log.info("worker.done")

if __name__ == "__main__":
    main()
