import time
import sys
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from db import create_tables, heartbeat

def beat():
    try:
        heartbeat("worker", "alive")
        print("beat OK")
    except Exception as e:
        print("beat ERROR:", e)
        traceback.print_exc(file=sys.stdout)

def main():
    try:
        create_tables()
        print("tables OK")
    except Exception as e:
        print("create_tables ERROR:", e)
        traceback.print_exc(file=sys.stdout)

    sch = BackgroundScheduler(timezone="UTC", daemon=False)
    sch.add_job(
        beat,
        "interval",
        seconds=60,
        id="heartbeat",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
    )
    sch.start()
    print("scheduler started")

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
