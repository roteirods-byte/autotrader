import os
from sqlalchemy import create_engine, text

# Usa a URL do Postgres que você colocou no Render (Ambiente -> DATABASE_URL)
DATABASE_URL = os.environ["DATABASE_URL"]

# Conexão resiliente (detecta conexão quebrada e recicla)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10},
    future=True,
)

def create_tables():
    ddl = """
    CREATE TABLE IF NOT EXISTS heartbeats(
        id bigserial PRIMARY KEY,
        source text NOT NULL,
        status text NOT NULL,
        created_at timestamptz NOT NULL DEFAULT now()
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))

def heartbeat(source: str, status: str):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO heartbeats(source, status) VALUES (:s, :t)"),
            {"s": source, "t": status},
        )
