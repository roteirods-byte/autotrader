import time
from apscheduler.schedulers.background import BackgroundScheduler
from db import create_tables, heartbeat

def beat():
    heartbeat("worker", "alive")

def main():
    create_tables()
    sch = BackgroundScheduler(timezone="UTC")
    sch.add_job(beat, "interval", seconds=60, id="heartbeat", replace_existing=True)
    sch.start()
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
