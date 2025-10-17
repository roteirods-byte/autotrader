from __future__ import annotations
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
# insere moedas ausentes
data, hora, iso = now_brt_str()
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
# PRAGMA table_info não aceita parâmetro bind. Usamos f-string
# com nome vindo de lista interna (whitelist) para segurança.
cur = conn.execute(f"PRAGMA table_info({name})")
# colunas: 0=cid, 1=name, 2=type, ...
existing = {row[1] for row in cur.fetchall()}
select_cols = [c for c in cols if c in existing]
if not select_cols:
return pd.DataFrame(columns=cols)
q = f"SELECT {', '.join(select_cols)} FROM {name}"
df = pd.read_sql_query(q, conn)
# Garante ordem e colunas vazias quando faltarem
for c in cols:
if c not in df.columns:
df[c] = None
return df[cols]
finally:
conn.close()
