# BLOCO 30 - INICIO (entrada.py)
import streamlit as st
import pandas as pd
from . import tokens as T
from .commons import inject_theme_css, page_header, section_title

def init_state():
    if T.SS_ENTRADA not in st.session_state:
        pairs = sorted(st.session_state.get(T.SS_COINS, pd.DataFrame({"Símbolo": T.DEFAULT_SYMBOLS}))["Símbolo"].tolist())
        def make_df():
            return pd.DataFrame({
                "PARIDADE": pairs,
                "SINAL": ["NÃO ENTRAR" for _ in pairs],
                "PREÇO": [0.0 for _ in pairs],
                "ALVO":  [0.0 for _ in pairs],
                "GANHO %":[0.0 for _ in pairs],
                "DATA":  ["" for _ in pairs],
                "HORA":  ["" for _ in pairs],
            })
        st.session_state[T.SS_ENTRADA] = { "SWING_4H": make_df(), "POSICIONAL_1H": make_df() }

def _format_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["PREÇO"] = df["PREÇO"].map(T.fmt_price)
    df["ALVO"]  = df["ALVO"].map(T.fmt_price)
    df["GANHO %"] = df["GANHO %"].map(T.fmt_pct)
    return df

def render():
    inject_theme_css()
    page_header()
    section_title("ENTRADA")

    init_state()
    data = st.session_state[T.SS_ENTRADA]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ENTRADA 4H — SWING")
        st.dataframe(_format_df(data["SWING_4H"]), use_container_width=True, height=540)
    with c2:
        st.subheader("ENTRADA 1H — POSICIONAL")
        st.dataframe(_format_df(data["POSICIONAL_1H"]), use_container_width=True, height=540)
# BLOCO 30 - FIM
