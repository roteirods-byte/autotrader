# aplicativo.py
from __future__ import annotations
import os, re, smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
from zoneinfo import ZoneInfo
from datetime import datetime
from db import get_engine, ensure_tables, fetch_table, list_required_coins

# ============== Config ==============
TZ = os.getenv("TZ", "America/Sao_Paulo")
st.set_page_config(page_title="Painéis | EMAIL • MOEDAS • ENTRADA • SAÍDA", layout="wide")

# ============== CSS global (padrão visual) ==============
st.markdown("""
<style>
:root { --orange:#ff8c00; }

/* Abas em abóbora */
button[data-baseweb="tab"] p{ color:var(--orange) !important; font-weight:700; }
button[aria-selected="true"]{ border-bottom:3px solid var(--orange) !important; }

/* Títulos / rótulos laranja */
h3.title-orange{ color:var(--orange); margin:0 0 .6rem 0; }
.label-orange{ color:var(--orange); font-weight:700; margin:.25rem 0 .25rem; }

/* Linha de inputs: gap 20px e inputs com 250px */
div[data-testid="stHorizontalBlock"]{ gap:20px !important; }
div[data-testid="stTextInput"] input{ width:250px !important; }

/* Tabela: remover toolbar/índice e ajustar header/cor/alinhamento */
div[data-testid="stElementToolbar"]{ display:none !important; }
.email-wrap{ max-width:1306px; width:1306px; margin-left:0; }
div[data-testid="stDataFrame"] thead th{
  color:var(--orange) !important; text-align:center !important;
}
div[data-testid="stDataFrame"] thead th div{ justify-content:center !important; }
div[data-testid="stDataFrame"] tbody td:nth-child(1),
div[data-testid="stDataFrame"] thead th:nth-child(1){ width:90px !important; text-align:center; }
div[data-testid="stDataFrame"] tbody td:nth-child(2),
div[data-testid="stDataFrame"] thead th:nth-child(2){ width:90px !important; text-align:center; }

/* Tipografia da grid e legenda */
div[data-testid="stDataFrame"] div[role="grid"]{ font-size:.95rem; }
.footer-note{ opacity:.6; font-size:.85rem; }
.badge-long{ color:#00E676; font-weight:700; }
.badge-short{ color:#FF5252; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ============== Helpers ==============
def fmt_prices(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
    return df
def fmt_perc(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
    return df
def now_brt_str() -> str: return datetime.now(ZoneInfo(TZ)).strftime("%d/%m/%Y %H:%M:%S")
def is_email(x:str)->bool: return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", x))
def send_email_gmail(user:str, app_password:str, to:str, subject:str, body:str):
    msg = MIMEText(body, "plain", "utf-8"); msg["Subject"]=subject; msg["From"]=user; msg["To"]=to
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
        s.ehlo(); s.starttls(); s.login(user, app_password); s.send_message(msg)

# ============== Dados (somente banco) ==============
engine = get_engine(); ensure_tables(engine)

emails = fetch_table("emails", engine)
if emails.empty:
    emails = pd.DataFrame([{"data":"", "hora":"", "assunto":"", "mensagem":"", "status":""}])

moedas = fetch_table("moedas", engine)
if moedas.empty:
    moedas = pd.DataFrame({"simbolo": sorted(list_required_coins()), "ativo": True, "observacao": ""})
else:
    moedas = moedas.sort
