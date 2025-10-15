# worker.py
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Tenta usar as funções do db.py (create_tables e heartbeat).
# Se não existir, cai no "plano B" (apenas logs) para não travar o worker.
try:
    from db import create_tables, heartbeat
except Exception as e:
    def create_tables():
        logging.warning("db.create_tables() não disponível: %s", e)

    def heartbeat(source: str, status: str):
        logging.info("HEARTBEAT(%s=%s) (stub)", source, status)

# Logs no console (o Render mostra isso nos Logs).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    force=True,
)

def beat():
    """Envia um sinal de vida a cada minuto."""
    try:
        heartbeat("worker", "alive")
        logging.info("Beat OK")
    except Exception as ex:
        logging.exception("Beat failed: %s", ex)

def main():
    logging.info("Starting worker...")
    # Cria as tabelas (se a função existir no db.py)
    try:
        create_tables()
        logging.info("Tables OK")
    except Exception as ex:
        logging.exception("create_tables failed: %s", ex)

    # Agenda o beat a cada 60s
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(beat, "interval", seconds=60, id="heartbeat", replace_existing=True)
    scheduler.start()

    logging.info("Worker running. Sleeping loop.")
    # Loop simples para manter o processo vivo
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logging.info("Stopping worker...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
