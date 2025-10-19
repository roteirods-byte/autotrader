# autotrader/db_bootstrap.py
import os
import psycopg2

def ensure_email_table():
    url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_config (
            id SERIAL PRIMARY KEY,
            principal TEXT NOT NULL,
            app_password TEXT NOT NULL,
            enviar_para TEXT NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
    )
    cur.close()
    conn.close()
