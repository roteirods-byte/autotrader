from __future__ import annotations
import pandas as pd
from db import init_db, fetch_table




def test_init_and_fetch_tables(tmp_path):
db_path = tmp_path / "test.db"
# usa variável de ambiente via monkeypatch no CI se necessário; aqui chamamos direto
init_db(db_path)
for name in ["emails", "moedas", "entradas", "saidas"]:
df = fetch_table(name, db_path)
assert isinstance(df, pd.DataFrame)
assert df.columns.size > 0
