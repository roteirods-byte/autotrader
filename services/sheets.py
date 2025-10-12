# services/sheets.py
import os, gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def _gc():
    cred_path = os.environ.get("GCP_CREDENTIALS_PATH")
    if not cred_path:
        raise RuntimeError("Defina GCP_CREDENTIALS_PATH com o caminho do JSON.")
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

def _ws(sheet_id, tab):
    gc = _gc()
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows=200, cols=10)
    return ws

def get_moedas(sheet_id):
    ws = _ws(sheet_id, "MOEDA")
    # coluna A a partir da linha 2 (linha 1 é cabeçalho "PAR")
    vals = ws.col_values(1)[1:]
    moedas = [v.strip().upper() for v in vals if v.strip()]
    # corrige erro comum "BNC" -> "BNB"
    moedas = ["BNB" if m == "BNC" else m for m in moedas]
    # remove duplicados e ordena
    return sorted(set(moedas))

def save_moedas(sheet_id, moedas):
    ws = _ws(sheet_id, "MOEDA")
    # limpa A2:A
    ws.batch_clear(["A2:A"])
    if moedas:
        data = [[m] for m in sorted(set(moedas))]
        ws.update("A2", data, value_input_option="USER_ENTERED")

def seed_moedas(sheet_id, default_list):
    # sobrescreve a coluna A com a lista padrão
    save_moedas(sheet_id, default_list)
