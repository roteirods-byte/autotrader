from __future__ import annotations
import streamlit as st
from autotrader.db_bootstrap import ensure_email_table
from autotrader.panels.email_panel import render as render_email_panel
import pandas as pd
from db import init_db, fetch_table
from ui.theme import apply_theme

st.set_page_config(page_title="Autotrader", layout="wide")
apply_theme()

# Inicializa DB local (arquivo) — não chama serviços externos
init_db()

st.title("Painéis da Automação")

# EMAIL
st.subheader("EMAIL")
with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    df_email = fetch_table("emails")
    if df_email.empty:
        df_email = pd.DataFrame(
            columns=[
                "moeda","side","preco_atual","alvo","pl_pct","data","hora","status","assunto","mensagem","modo"
            ]
        )
    st.dataframe(df_email, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# MOEDAS
st.subheader("MOEDAS")
with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    df_coins = fetch_table("moedas")
    if not df_coins.empty:
        df_coins = df_coins.sort_values("simbolo")
    else:
        df_coins = pd.DataFrame(columns=["simbolo","ativo","observacao","created_at","updated_at"])
    st.dataframe(df_coins, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ENTRADA (Swing e Posicional lado a lado)
st.subheader("ENTRADA")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Swing (ATR 4H)**")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    df_e = fetch_table("entradas")
    st.dataframe(df_e, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("**Posicional (ATR 1D)**")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.dataframe(df_e, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# SAÍDA
st.subheader("SAÍDA")
with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    df_s = fetch_table("saidas")
    if df_s.empty:
        df_s = pd.DataFrame(
            columns=[
                "data","hora","moeda","side","modo","preco_entrada","preco_atual","alvo","pnl_pct","situacao"
            ]
        )
    st.dataframe(df_s, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
