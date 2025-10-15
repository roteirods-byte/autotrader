# db.py — engine preguiçoso e operações seguras

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

_ENGINE = None

def _get_engine():
    """Cria o engine apenas na primeira vez (lazy) e reaproveita depois."""
    global _ENGINE
    if _ENGINE is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL não configurado")
        # Pool pequeno evita estouro no plano Starter
        _ENGINE = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=0,
            future=True,
        )
    return _ENGINE

def create_tables():
    """Cria a tabela de heartbeat se ainda não existir."""
    try:
        eng = _get_engine()
        with eng.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS heartbeat (
                  id SERIAL PRIMARY KEY,
                  source VARCHAR(50) NOT NULL,
                  at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))
        print("tables OK", flush=True)
    except Exception as e:
        print("create_tables ERROR:", e, flush=True)
        # reergue para o caller decidir se continua ou não
        raise

def heartbeat(source, status):
    """Registra um batimento para monitorar se o worker está vivo."""
    try:
        eng = _get_engine()
        with eng.begin() as conn:
            conn.execute(
                text("INSERT INTO heartbeat (source, at) VALUES (:s, now())"),
                {"s": f"{source}:{status}"}
            )
        print("beat OK", flush=True)
    except Exception as e:
        print("heartbeat ERROR:", e, flush=True)
        # reergue para o caller decidir se continua ou não
        raise
