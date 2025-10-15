# services/sheets.py
from __future__ import annotations
import os, json
from typing import Any, List, Dict

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

DEFAULT_TICKERS: List[str] = sorted([
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT","ETH","FET","FIL","FLUX",
    "ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB","SOL",
    "SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
])

def _load_sa_info() -> Dict[str, Any]:
    raw = os.getenv("GOOGLE_SA_JSON")
    path = os.getenv("GOOGLE_SA_PATH")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError("GOOGLE_SA_JSON inválido (não é JSON).")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError("Credencial ausente: defina GOOGLE_SA_JSON ou GOOGLE_SA_PATH.")

def get_client() -> gspread.Client:
    sa_info = _load_sa_info()
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return gspread.authorize(creds)

def open_by_key(sheet_id: str):
    return get_client().open_by_key(sheet_id)

def read_worksheet(sheet_id: str, ws_name: str) -> List[List[Any]]:
    sh = open_by_key(sheet_id)
    ws = sh.worksheet(ws_name)
    return ws.get_all_values()

def write_rows(sheet_id: str, ws_name: str, rows: List[List[Any]], clear: bool = False) -> None:
    sh = open_by_key(sheet_id)
    try:
        ws = sh.worksheet(ws_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=ws_name, rows=max(100, len(rows)+10), cols=max(20, len(rows[0]) if rows else 20))
    if clear:
        ws.clear()
    if rows:
        ws.update("A1", rows)
