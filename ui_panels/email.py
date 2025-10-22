# BLOCO 10 - INICIO (email.py)
import streamlit as st
from .tokens import SS_EMAIL
from . import tokens as T
from .commons import inject_theme_css, page_header, section_title, email_container_open, container_close

def init_state():
    if SS_EMAIL not in st.session_state:
        st.session_state[SS_EMAIL] = {"principal": "", "senha": "", "envio": ""}

def render():
    inject_theme_css()
    page_header()
    section_title("CORREIO ELETRÔNICO")
    init_state()
    cfg = st.session_state[SS_EMAIL]

    email_container_open()
    c1,c2,c3,c4 = st.columns([3,2,3,2])
    with c1:
        cfg["principal"] = st.text_input("Principal:", value=cfg["principal"], key="email_principal")
    with c2:
        cfg["senha"] = st.text_input("Senha:", value=cfg["senha"], type="password", key="email_senha")
    with c3:
        cfg["envio"] = st.text_input("Envio:", value=cfg["envio"], key="email_envio")
    with c4:
        salvar = st.button("TESTAR/SALVAR", use_container_width=True)
    container_close()

    if salvar:
        st.session_state[SS_EMAIL] = cfg
        st.success(f"E-mail de teste enviado para {cfg['envio']} (simulado).")
# BLOCO 10 - FIM
