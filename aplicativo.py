# aplicativo.py
from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from zoneinfo import ZoneInfo
from datetime import datetime

from db import get_engine, ensure_tables, fetch_table, list_required_coins

# ===== Configurações básicas =====
TZ = os.getenv("TZ", "America/Sao_Paulo")

st.set_page_config(
    page_title="Painéis | EMAIL • MOEDAS • ENTRADA • SAÍDA",
    layout="wide",
)

# ===== Estilo (cores e detalhes visuais) =====
CSS = """
<style>
div[data-testid="stDataFrame"] div[role="grid"] { font-size: 0.95rem; }
.badge-long { color: #00E676; font-weight: 700; }
.badge-short { color: #FF5252; font-weight: 700; }
.footer-note { opacity: 0.6; font-size: 0.85rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ===== Helpers de formato =====
def fmt_prices(df: pd.DataFrame, price_cols: list[str]) -> pd.DataFrame:
    for c in price_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
    return df

def fmt_perc(df: pd.DataFrame, perc_cols: list[str]) -> pd.DataFrame:
    for c in perc_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
    return df

def now_brt_str() -> str:
    return datetime.now(ZoneInfo(TZ)).strftime("%d/%m/%Y %H:%M:%S")

# ===== Dados (somente leitura do BANCO) =====
# IMPORTANTE: esta versão NÃO lê Google Sheets -> não usa credenciais.
engine = get_engine()
ensure_tables(engine)

# EMAIL
emails = fetch_table("emails", engine)
if emails.empty:
    emails = pd.DataFrame([{"data":"", "hora":"", "assunto":"", "mensagem":"", "status":""}])

# MOEDAS
moedas = fetch_table("moedas", engine)
if moedas.empty:
    moedas = pd.DataFrame({"simbolo": sorted(list_required_coins()), "ativo": True, "observacao": ""})
else:
    moedas = moedas.sort_values(by="simbolo", ascending=True)

# ENTRADA
entradas = fetch_table("entradas", engine)
if entradas.empty:
    entradas = pd.DataFrame([{
        "data":"", "hora":"", "moeda":"", "side":"", "preco_entrada":"", "stop":"", "tp":"", "score":"", "modo":""
    }])
entradas = fmt_prices(entradas, ["preco_entrada","stop","tp"])
entradas = fmt_perc(entradas, ["score"])

# SAÍDA
saidas = fetch_table("saidas", engine)
if saidas.empty:
    saidas = pd.DataFrame([{
        "data":"", "hora":"", "moeda":"", "side":"", "modo":"", "entrada":"", "preco_atual":"", "alvo":"", "pnl_pct":"", "situacao":""
    }])
saidas = fmt_prices(saidas, ["entrada","preco_atual","alvo"])
saidas = fmt_perc(saidas, ["pnl_pct"])

# ===== Layout =====
st.title("📊 Painéis do Operador — EMAIL • MOEDAS • ENTRADA • SAÍDA")
st.caption(f"Atualizado: {now_brt_str()} (BRT). Visual padronizado. *Somente leitura.*")

tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["✉️ EMAIL", "🪙 MOEDAS", "✅ ENTRADA", "📤 SAÍDA"])

with tab_email:
    st.subheader("EMAIL")
    st.dataframe(
        emails[["data","hora","assunto","mensagem","status"]].fillna(""),
        use_container_width=False,
        width=1306,
        height=160
    )
    st.markdown('<div class="footer-note">Painel EMAIL — 1306×160 px | % com 2 casas • preços 3 casas • Data/Hora separadas.</div>', unsafe_allow_html=True)

with tab_moedas:
    st.subheader("MOEDAS (A–Z)")
    st.dataframe(
        moedas[["simbolo","ativo","observacao"]].fillna(""),
        use_container_width=True,
        height=420
    )
    st.markdown('<div class="footer-note">Sem coluna “alavancagem”. Ordem alfabética A–Z.</div>', unsafe_allow_html=True)

with tab_entrada:
    st.subheader("ENTRADA (somente leitura)")
    cols = ["data","hora","moeda","side","preco_entrada","stop","tp","score","modo"]
    view = entradas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">LONG <span class="badge-long">verde</span> • SHORT <span class="badge-short">vermelho</span>. '
        'Preços 3 casas • % 2 casas • Data/Hora separadas.</div>',
        unsafe_allow_html=True
    )

with tab_saida:
    st.subheader("SAÍDA (somente leitura)")
    cols = ["data","hora","moeda","side","modo","entrada","preco_atual","alvo","pnl_pct","situacao"]
    view = saidas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">Campos: moeda, side, modo, entrada, preço atual, alvo, PnL%, situação, data, hora.</div>',
        unsafe_allow_html=True
    )
