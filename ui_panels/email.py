# BLOCO 10 - INICIO (email.py)
import streamlit as st
from .tokens import SS_EMAIL
from . import tokens as T
from .commons import inject_theme_css, page_header, section_title

def init_state():
    if SS_EMAIL not in st.session_state:
        st.session_state[SS_EMAIL] = {"principal": "", "senha": "", "envio": ""}

def render():
    inject_theme_css()
    page_header()
    section_title("CORREIO ELETRÔNICO")
    init_state()
    cfg = st.session_state[SS_EMAIL]

    # Cartão do EMAIL com 1306x160 e linha de 4 caixas (260px) com gap 40px
    st.markdown("<div class='email-card'><div class='email-row'>", unsafe_allow_html=True)

    # Coluna 1 — Principal
    with st.container():
        st.markdown("<div class='col'>", unsafe_allow_html=True)
        cfg["principal"] = st.text_input("Principal:", value=cfg["principal"], key="email_principal")
        st.markdown("</div>", unsafe_allow_html=True)

    # Coluna 2 — Senha
    with st.container():
        st.markdown("<div class='col'>", unsafe_allow_html=True)
        cfg["senha"] = st.text_input("Senha:", value=cfg["senha"], type="password", key="email_senha")
        st.markdown("</div>", unsafe_allow_html=True)

    # Coluna 3 — Envio
    with st.container():
        st.markdown("<div class='col'>", unsafe_allow_html=True)
        cfg["envio"] = st.text_input("Envio:", value=cfg["envio"], key="email_envio")
        st.markdown("</div>", unsafe_allow_html=True)

    # Coluna 4 — Botão
    with st.container():
        st.markdown("<div class='col'>", unsafe_allow_html=True)
        salvar = st.button("TESTAR/SALVAR", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    if salvar:
        st.session_state[SS_EMAIL] = cfg
        st.success(f"E-mail de teste enviado para {cfg['envio']} (simulado).")
# BLOCO 10 - FIM
