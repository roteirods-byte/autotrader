from __future__ import annotations
from pathlib import Path
import pandas as pd
from db import init_db, fetch_table


def test_init_and_fetch(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    for name in ["emails", "moedas", "entradas", "saidas"]:
        df = fetch_table(name, db_path)
        assert isinstance(df, pd.DataFrame)
