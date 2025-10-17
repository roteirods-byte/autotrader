from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from typing import List
from datetime import datetime
import pandas as pd
import pytz

TZ = os.getenv("TZ", "America/Sao_Paulo")
DB_PATH = os.getenv("DB_PATH", "autotrader.db")

SCHEMA_SQL = r"""
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS moedas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  simbolo TEXT NOT NULL UNIQUE,
  ativo INTEGER NOT NULL DEFAULT 1,
  observacao TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  moeda TEXT NOT NULL,
  side TEXT CHECK(side IN ('LONG','SHORT')),
  preco_atual REAL,
  alvo REAL,
  pl_pct REAL,
  modo TEXT CHECK(modo IN ('SWING','POSICIONAL')),
  assunto TEXT,
  mensagem TEXT,
  status TEXT,
  data TEXT NOT NULL,
  hora TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entradas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data TEXT NOT NULL,
  hora TEXT NOT NULL,
  moeda TEXT NOT NULL,
  side TEXT CHECK(side IN ('LONG','SHORT')),
  preco_entrada REAL,
  alvo REAL,
  score REAL,
  modo TEXT CHECK(modo IN ('SWING','POSICIONAL')),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saidas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data TEXT NOT NULL,
  hora TEXT NOT NULL,
  moeda TEXT NOT NULL,
  side TEXT CHECK(side IN ('LONG','SHORT')),
  modo TEXT CHECK(modo IN ('SWING','POSICIONAL')),
  preco_entrada REAL,
  preco_atual REAL,
  alvo REAL,
  pnl_pct REAL,
  situacao TEXT,
  created_at TEXT NOT NULL
);
"""

PANEL_COLUMNS = {
    "emails": [
        "moeda",
        "side",
        "preco_atual",
        "alvo",
        "pl_pct",
        "data",
        "hora",
        "status",
        "assunto",
        "mensagem",
        "modo",
    ],
    "moedas": ["simbolo", "ativo", "observacao", "created_at", "updated_at"],
    "entradas": [
        "data",
        "hora",
        "moeda",
        "side",
        "preco_entrada",
        "alvo",
        "score",
        "modo",
    ],
    "saidas": [
        "data",
        "hora",
        "moeda",
        "side",
        "modo",
        "preco_entrada",
        "preco_atual",
        "alvo",
        "pnl_pct",
        "situacao",
    ],
}

REQUIRED_COINS: List[str] = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK",
    "LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB",
    "SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP",
]


def now_brt_str() -> tuple[str, str, str]:
    tz = pytz.timezone(TZ)
    dt = datetime.now(tz)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S"), dt.isoformat()


def get_conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        seed_moedas(conn)
        conn.commit()
    finally:
        conn.close()


def seed_moedas(conn: sqlite3.Connection) -> None:
    _, _, iso = now_brt_str()
    for sym in REQUIRED_COINS:
        conn.execute(
            """
            INSERT INTO moedas(simbolo, ativo, created_at)
            VALUES(?, 1, ?)
            ON CONFLICT(simbolo) DO NOTHING
            """,
            (sym, iso),
        )


def fetch_table(name: str, db_path: str | Path = DB_PATH) -> pd.DataFrame:
    name = name.lower()
    cols = PANEL_COLUMNS.get(name)
    if not cols:
        return pd.DataFrame()
    conn = get_conn(db_path)
    try:
        cur = conn.execute(f"PRAGMA table_info({name})")
        existing = {row[1] for row in cur.fetchall()}  # 1=name
        select_cols = [c for c in cols if c in existing]
        if not select_cols:
            return pd.DataFrame(columns=cols)
        q = f"SELECT {', '.join(select_cols)} FROM {name}"
        df = pd.read_sql_query(q, conn)
        for c in cols:
            if c not in df.columns:
                df[c] = None
        return df[cols]
    finally:
        conn.close()
