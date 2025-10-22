# BLOCO 10 - INICIO (panels/email.py)
import streamlit as st
from pydantic import ValidationError
from services import get_email_cfg, save_email_cfg
from schemas import EmailCfg

def render():
    st.markdown("<div class='section'>CORREIO ELETRÔNICO</div>", unsafe_allow_html=True)

    cfg = get_email_cfg()
    principal_val = cfg.principal if cfg else ""
    envio_val = cfg.envio if cfg else ""

    # cartão em largura fixa 1306 com 4 colunas 260px e gap 40px (forçado por CSS)
    st.markdown("<div class='email-card'><div class='email-row'>", unsafe_allow_html=True)

    st.markdown("<div class='email-col'>", unsafe_allow_html=True)
    principal = st.text_input("Principal:", value=principal_val, key="email_principal_v2")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='email-col'>", unsafe_allow_html=True)
    senha = st.text_input("Senha:", value="", type="password", key="email_senha_v2")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='email-col'>", unsafe_allow_html=True)
    envio = st.text_input("Envio:", value=envio_val, key="email_envio_v2")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='email-col'>", unsafe_allow_html=True)
    salvar = st.button("TESTAR/SALVAR", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    if salvar:
        try:
            # valida e salva (senha fica em st.secrets no futuro; não grava em DB)
            data = EmailCfg(principal=principal, envio=envio)
            save_email_cfg(data)
            st.success(f"Configurações salvas. Teste simulado enviado para {envio}.")
        except ValidationError as e:
            st.error("Dados inválidos. Verifique os e-mails.")
# BLOCO 10 - FIM
