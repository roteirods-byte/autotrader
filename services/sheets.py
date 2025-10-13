# src/services/sheets.py
import os
from functools import lru_cache
from typing import List, Optional

import gspread
from google.oauth2.service_account import Credentials

# Escopos necessários (Sheets + Drive)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---- Lista padrão (39) caso a planilha não esteja acessível ----
# Sem sufixo USDT, ordem alfabética.
DEFAULT_TICKERS: List[str] = sorted([
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB",
    "BTC","DOGE","DOT","ETC","ETH","FIL","FTM","GALA","ICP",
    "INJ","LDO","LINK","LTC","MANA","MATIC","NEAR","OP","PEPE",
    "RNDR","RUNE","SHIB","SOL","SUI","TIA","TON","TRX","UNI",
    "XLM","XMR","XRP"
])

def _normalize(t: str) -> str:
    """Normaliza: maiúsculas, remove espaços e sufixos '/USDT'|'USDT'."""
    t = (t or "").upper().strip()
    if not t:
        return ""
    for suf in ["/USDT", "USDT"]:
        if t.endswith(suf):
            t = t[: -len(suf)].strip().rstrip("/")
    return t

# ---------- Autenticação (cacheada) ----------
@lru_cache(maxsize=1)
def _gc() -> gspread.Client:
    cred_path = os.getenv("GCP_CREDENTIALS_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError(
            "Defina GCP_CREDENTIALS_PATH (ou GOOGLE_APPLICATION_CREDENTIALS) "
            "com o caminho do JSON da conta de serviço."
        )
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

def _ws(tab_name: str, sheet_id: Optional[str] = None) -> gspread.Worksheet:
    sid = (sheet_id or os.getenv("SHEET_ID", "")).strip()
    if not sid:
        raise RuntimeError("SHEET_ID não definido.")
    return _gc().open_by_key(sid).worksheet(tab_name)

# ---------- API pública ----------
def get_moedas(sheet_id: Optional[str] = None) -> List[str]:
    """
    Lê a aba 'MOEDA' (coluna A) a partir da linha 2 (linha 1 = cabeçalho 'PAR').
    Se der erro (credencial/aba/ID), devolve DEFAULT_TICKERS (39).
    """
    try:
        ws = _ws("MOEDA", sheet_id)
        values = ws.col_values(1)[1:]  # linha 1 = cabeçalho
        cleaned = [_normalize(v) for v in values if _normalize(v)]
        return sorted(list(dict.fromkeys(cleaned)))
    except Exception:
        return DEFAULT_TICKERS[:]

def save_moedas(moedas: List[str], sheet_id: Optional[str] = None) -> None:
    """
    Salva a lista na aba 'MOEDA' (coluna A), com cabeçalho 'PAR' na linha 1.
    """
    ws = _ws("MOEDA", sheet_id)
    moedas_clean = sorted(list(dict.fromkeys([_normalize(m) for m in moedas if _normalize(m)])))
    data = [["PAR"]] + [[m] for m in moedas_clean]
    ws.clear()
    ws.update(f"A1:A{len(data)}", data)
