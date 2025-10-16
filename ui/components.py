# ui/components.py
from __future__ import annotations
import streamlit as st
import pandas as pd

def tokens():
    return st.session_state.get("__ui_tokens", {})

def title(texto: str, level: int = 3):
    st.markdown(f'<h{level} class="title-orange">{texto}</h{level}>', unsafe_allow_html=True)

def form_row(label: str, key: str, value: str = "", password: bool = False):
    # Renderiza rótulo laranja + input (250px via CSS)
    st.markdown(f'<div class="label-orange">{label}</div>', unsafe_allow_html=True)
    return st.text_input("", value=value, key=key, type=("password" if password else "default"),
                         label_visibility="collapsed")

def email_table(df: pd.DataFrame):
    t = tokens()
    w = t.get("tabela_email", {}).get("largura_px", 1306)
    h = t.get("tabela_email", {}).get("altura_px", 160)
    st.markdown('<div class="email-wrap">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=False, width=w, height=h, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
