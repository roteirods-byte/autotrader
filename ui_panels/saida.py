# BLOCO 40 - INICIO (saida.py)
import streamlit as st
import pandas as pd
from . import tokens as T
from .commons import inject_theme_css, page_header, section_title

COLS = ["PARIDADE","LADO","MODO","ENTRADA","ALVO","PREÇO ATUAL","% de PNL","SITUAÇÃO","DADOS","HORA","ALAV","EXCLUIR"]

def init_state():
    if T.SS_SAIDA not in st.session_state:
        st.session_state[T.SS_SAIDA] = pd.DataFrame(columns=COLS)

def calc_pnl_pct(row):
    try:
        entrada = float(row.get("ENTRADA", 0) or 0)
        preco   = float(row.get("PREÇO ATUAL", 0) or 0)
        lado    = row.get("LADO","LONGAS")
        if entrada == 0:
            return 0.0
        if lado == "LONGAS":
            return (preco/entrada - 1.0) * 100.0
        else:
            return (entrada/preco - 1.0) * 100.0
    except Exception:
        return 0.0

def render():
    inject_theme_css()
    page_header()
    section_title("SAÍDA")
    init_state()

    coins_df = st.session_state.get(T.SS_COINS, None)
    pairs = (coins_df["Símbolo"].tolist() if coins_df is not None else T.DEFAULT_SYMBOLS)

    with st.container():
        c1,c2,c3,c4,c5 = st.columns([1.2,1,1.2,1,1])
        par   = c1.selectbox("Par", options=pairs, index=0)
        lado  = c2.radio("Lado", options=["LONGAS","CURTO"], horizontal=True)
        modo  = c3.selectbox("Modo", options=["SWING","POSICIONAL"])
        ent   = c4.number_input("Entrada", value=0.0, step=0.001, format="%.3f")
        alav  = c5.number_input("Alav", value=5, min_value=1, step=1)

    add = st.button("Adicionar Operação")
    if add:
        data, hora = T.today_date_time()
        new = {
            "PARIDADE": par, "LADO": lado, "MODO": modo,
            "ENTRADA": ent, "ALVO": 0.0, "PREÇO ATUAL": 0.0,
            "% de PNL": 0.0, "SITUAÇÃO": "", "DADOS": data, "HORA": hora,
            "ALAV": alav, "EXCLUIR": False
        }
        st.session_state[T.SS_SAIDA] = pd.concat([st.session_state[T.SS_SAIDA], pd.DataFrame([new])], ignore_inde
x=True)

    df = st.session_state[T.SS_SAIDA].copy()
    df["% de PNL"] = df.apply(calc_pnl_pct, axis=1)
    if "ENTRADA" in df: df["ENTRADA"] = df["ENTRADA"].map(T.fmt_price)
    if "ALVO" in df: df["ALVO"] = df["ALVO"].map(T.fmt_price)
    if "PREÇO ATUAL" in df: df["PREÇO ATUAL"] = df["PREÇO ATUAL"].map(T.fmt_price)
    df["% de PNL"] = df["% de PNL"].map(T.fmt_pct)

    st.dataframe(df, use_container_width=True, height=520)
# BLOCO 40 - FIM
