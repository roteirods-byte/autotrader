# db.py
from __future__ import annotations
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DEFAULT_SQLITE = "sqlite:///local.db"

def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
    # Tipos: postgresql+psycopg2://user:pass@host:5432/db
    engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5, future=True)
    return engine

DDL = """
CREATE TABLE IF NOT EXISTS heartbeats (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    app_version TEXT
);
CREATE TABLE IF NOT EXISTS emails (
    id BIGSERIAL PRIMARY KEY,
    data DATE,
    hora TIME,
    assunto TEXT,
    mensagem TEXT,
    status TEXT
);
CREATE TABLE IF NOT EXISTS moedas (
    id BIGSERIAL PRIMARY KEY,
    simbolo TEXT UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    observacao TEXT
);
CREATE TABLE IF NOT EXISTS entradas (
    id BIGSERIAL PRIMARY KEY,
    data DATE,
    hora TIME,
    moeda TEXT,
    side TEXT,           -- LONG/SHORT
    preco_entrada NUMERIC,
    stop NUMERIC,
    tp NUMERIC,
    score NUMERIC,
    modo TEXT            -- swing/posicional
);
CREATE TABLE IF NOT EXISTS saidas (
    id BIGSERIAL PRIMARY KEY,
    data DATE,
    hora TIME,
    moeda TEXT,
    side TEXT,
    modo TEXT,
    entrada NUMERIC,
    preco_atual NUMERIC,
    alvo NUMERIC,
    pnl_pct NUMERIC,
    situacao TEXT        -- ganho/perda/fechado/aberto
);
"""

def ensure_tables(engine: Engine | None = None) -> None:
    engine = engine or get_engine()
    with engine.begin() as conn:
        for stmt in DDL.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))

def upsert_heartbeat(engine: Engine | None = None, app_version: str | None = None) -> None:
    engine = engine or get_engine()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO heartbeats (app_version) VALUES (:v)"), {"v": app_version})

def fetch_table(table: str, engine: Engine | None = None) -> pd.DataFrame:
    engine = engine or get_engine()
    try:
        return pd.read_sql(f"SELECT * FROM {table} ORDER BY id DESC", engine)
    except Exception:
        return pd.DataFrame()

def list_required_coins() -> list[str]:
    # Universo fixo de 39 moedas (ordem A–Z)
    return [
        "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT","ETH","FET","FIL","FLUX",
        "ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB","SOL",
        "SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
    ]
