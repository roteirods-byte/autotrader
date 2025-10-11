# services/sheets.py
import os
from functools import lru_cache
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@lru_cache(maxsize=1)
def _gc():
    cred_path = os.getenv("GCP_CREDENTIALS_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError("Defina GCP_CREDENTIALS_PATH com o caminho do JSON.")
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

def _ws(tab_name: str):
    sid = os.getenv("SHEET_ID", "").strip()
    if not sid:
        raise RuntimeError("SHEET_ID não definido.")
    return _gc().open_by_key(sid).worksheet(tab_name)

# -------- Moedas --------
def get_moedas():
    ws = _ws("MOEDA")
    # Lê coluna A (PAR), ignorando cabeçalho (linha 1)
    values = ws.col_values(1)[1:]
    tickers = []
    for v in values:
        t = v.strip().upper()
        if not t:
            continue
        # sem sufixo USDT por padrão
        t = t.replace("/USDT", "").replace("USDT", "")
        tickers.append(t)
    return sorted(set(tickers))

def save_moedas(tickers):
    ws = _ws("MOEDA")
    # Limpa A2:A1000 e grava novamente a lista (mantém cabeçalho na linha 1)
    ws.update("A2:A1000", [[""]]*999)
    data = [[t] for t in sorted(set([t.strip().upper() for t in tickers if t.strip()]))]
    if data:
        ws.update("A2", data, value_input_option="RAW")
