# worker.py
from __future__ import annotations
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from db import get_engine, ensure_tables, upsert_heartbeat

TZ = os.getenv("TZ", "America/Sao_Paulo")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

def job_heartbeat():
    # No futuro: pipeline de dados → indicadores → sinais → auditoria
    upsert_heartbeat(get_engine(), APP_VERSION)
    print(f"[{datetime.now(ZoneInfo(TZ)).isoformat()}] heartbeat OK - {APP_VERSION}")

def main():
    ensure_tables(get_engine())
    sched = BlockingScheduler(timezone=ZoneInfo(TZ))
    # A cada 15 minutos
    sched.add_job(job_heartbeat, CronTrigger(minute="*/10"))  # antes: */15
print("Worker iniciado (10 min)...")                      # ajuste do texto
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("Worker finalizado.")

if __name__ == "__main__":
    main()
