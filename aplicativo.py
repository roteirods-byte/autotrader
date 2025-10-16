# aplicativo.py (SUBSTITUA TODO O CONTEÚDO POR ESTE)

from __future__ import annotations
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from db import get_engine, ensure_tables, fetch_table, list_required_coins
from ui.theme import apply_theme  # <<< TEMA UI (cores/tamanhos centralizados)

# ======== Config da página ========
st.set_page_config(page_title="Painéis | EMAIL • MOEDAS • ENTRADA • SAÍDA", layout="wide")

# Injeta o tema (cor abóbora nos títulos/abas, largura inputs etc.)
_UI = apply_theme()

# ======== Estilo adicional do projeto (sem conflitar com o tema) ========
CSS = """
<style>
.badge-long  { color: #00E676; font-weight: 700; }  /* verde */
.badge-short { color: #FF5252; font-weight: 700; }  /* vermelho */
.footer-note { opacity: 0.6; font-size: 0.85rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ======== Helpers ========
TZ = os.getenv("TZ", "America/Sao_Paulo")

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

# ======== Dados (somente leitura) ========
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

# ======== Layout ========
st.title("📊 Painéis do Operador — EMAIL • MOEDAS • ENTRADA • SAÍDA")
st.caption(f"Atualizado: {now_brt_str()} (BRT). Somente leitura.")

tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["✉️ EMAIL", "🪙 MOEDAS", "✅ ENTRADA", "📤 SAÍDA"])

with tab_email:
    st.markdown('<h3 class="title-orange">CORREIO ELETRÔNICO</h3>', unsafe_allow_html=True)
    st.markdown('<div class="email-wrap">', unsafe_allow_html=True)
    st.dataframe(
        emails[["data","hora","assunto","mensagem","status"]].fillna(""),
        use_container_width=False,
        width=_UI.get("tabela_email", {}).get("largura_px", 1306),
        height=_UI.get("tabela_email", {}).get("altura_px", 160),
        hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-note">E-MAIL — 1306×160 px | % com 2 casas • preços com 3 casas • Data/Hora separadas.</div>', unsafe_allow_html=True)

with tab_moedas:
    st.markdown('<h3 class="title-orange">MOEDAS (A–Z)</h3>', unsafe_allow_html=True)
    st.dataframe(
        moedas[["simbolo","ativo","observacao"]].fillna(""),
        use_container_width=True,
        height=420
    )
    st.markdown('<div class="footer-note">Ordem alfabética A–Z. Sincronização da lista ocorre na etapa de engine.</div>', unsafe_allow_html=True)

with tab_entrada:
    st.markdown('<h3 class="title-orange">ENTRADA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","preco_entrada","stop","tp","score","modo"]
    view = entradas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">LONG em <span class="badge-long">verde</span> • SHORT em <span class="badge-short">vermelho</span>. '
        'Preços 3 casas • % 2 casas • Data/Hora separadas.</div>',
        unsafe_allow_html=True
    )

with tab_saida:
    st.markdown('<h3 class="title-orange">SAÍDA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","modo","entrada","preco_atual","alvo","pnl_pct","situacao"]
    view = saidas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">Campos: moeda, side, modo, entrada, preço atual, alvo, PnL%, situação, data, hora.</div>',
        unsafe_allow_html=True
    )
