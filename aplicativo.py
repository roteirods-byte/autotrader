# arquivo: aplicativo.py
# Autotrader — Painéis (Streamlit)
# Versão focada no painel "E-MAIL" conforme padrão visual do projeto.

from __future__ import annotations

import os
import html
import smtplib
from email.mime.text import MIMEText

import streamlit as st


# -----------------------------------------------------------------------------
# CONFIGURAÇÃO BÁSICA DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Autotrader — Painéis",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------------
# ESTILO/TEMA GLOBAL — cores, abas em abóbora, inputs 250px, espaçamento 50px
# -----------------------------------------------------------------------------
ACCENT = "#ff7b1b"  # abóbora do projeto

GLOBAL_CSS = f"""
<style>
:root {{ --accent: {ACCENT}; }}

/* Esconde menu e rodapé do Streamlit */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

/* Abas (st.tabs) — rótulos em abóbora */
.stTabs [data-baseweb="tab"] p {{
  color: var(--accent) !important;
  font-weight: 700;
}}
.stTabs [aria-selected="true"] p {{
  color: var(--accent) !important;
}}

/* Títulos/legendas em abóbora */
h1, h2, h3, h4, h5, h6,
label, .stMarkdown strong {{
  color: var(--accent) !important;
}}

/* Inputs com largura 250px e altura 40px */
div.stTextInput input,
div[data-testid="stPassword"] input,
textarea {{
  width: 250px !important;
  height: 40px !important;
}}

/* Dá um respiro de 50px entre os campos (lado direito) */
div.stTextInput, div[data-testid="stPassword"] {{
  padding-right: 50px !important;
}}

/* Botão do mesmo tamanho dos inputs */
div.stButton > button {{
  width: 250px !important;
  height: 40px !important;
  background: var(--accent) !important;
  color: #0b2337 !important;   /* contraste no fundo escuro */
  font-weight: 700 !important;
  border: 0 !important;
  border-radius: 6px !important;
}}

/* Linha divisória mais discreta */
hr {{ opacity: .15; }}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FUNÇÃO: Envio de e-mail de teste via Gmail SMTP
# -----------------------------------------------------------------------------
def enviar_email_teste(user: str, app_password: str, destinatario: str) -> tuple[bool, str]:
    """
    Envia um e-mail de teste usando Gmail (SMTP SSL porta 465).
    Retorna (ok, erro).
    """
    try:
        corpo = "✔️ Teste de e-mail do Autotrader — configuração salva com sucesso."
        msg = MIMEText(corpo)
        msg["Subject"] = "Autotrader — Teste de e-mail"
        msg["From"] = user
        msg["To"] = destinatario

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(user, app_password)
            s.sendmail(user, [destinatario], msg.as_string())

        return True, ""
    except Exception as exc:  # nunca deixa quebrar a interface
        return False, str(exc)


# -----------------------------------------------------------------------------
# CABEÇALHO
# -----------------------------------------------------------------------------
st.markdown("## PAINÉIS DA AUTOMAÇÃO")
st.markdown("---")

# -----------------------------------------------------------------------------
# ABAS
# -----------------------------------------------------------------------------
abas = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# =============================================================================
# ABA 1 — E-MAIL
# =============================================================================
with abas[0]:
    st.markdown("### E-MAIL")

    # Valores padrão: lê das variáveis de ambiente (Render) e permite sobrescrever na sessão.
    user_val = st.session_state.get("MAIL_USER") or os.getenv("MAIL_USER", "")
    pass_val = st.session_state.get("MAIL_APP_PASSWORD") or os.getenv("MAIL_APP_PASSWORD", "")
    to_val   = st.session_state.get("MAIL_TO") or os.getenv("MAIL_TO", "")

    # 3 campos + 1 coluna para botão/mensagem (alinhados na mesma linha)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.6])

    with c1:
        user_in = st.text_input("Principal:", value=user_val, key="ui_mail_user")

    with c2:
        pass_in = st.text_input("Senha:", value=pass_val, type="password", key="ui_mail_pass")

    with c3:
        to_in = st.text_input("Envio:", value=to_val, key="ui_mail_to")

    with c4:
        bt = st.button("TESTAR/SALVAR", key="btn_testar_salvar")
        msg = st.empty()  # mensagem aparece aqui, logo após o botão

    if bt:
        # Persiste no estado da sessão (para a página atual).
        # OBS: Para persistir "de verdade" (após reinício), é preciso salvar em DB/secrets/env.
        st.session_state["MAIL_USER"] = user_in
        st.session_state["MAIL_APP_PASSWORD"] = pass_in
        st.session_state["MAIL_TO"] = to_in

        ok, erro = enviar_email_teste(user_in, pass_in, to_in)
        if ok:
            msg.success("Configuração salva e e-mail de teste enviado ✅")
        else:
            # Escapa HTML para não quebrar a página (corrige aquele SyntaxError do print)
            msg.error(f"Falha ao salvar/testar e-mail: {html.escape(erro)}")

    st.markdown("---")


# =============================================================================
# ABA 2 — MOEDAS (placeholder seguro por enquanto)
# =============================================================================
with abas[1]:
    st.markdown("### MOEDAS")
    st.info("Painel de MOEDAS será ajustado após concluirmos o E-MAIL. (Placeholder seguro.)")
    st.markdown("---")


# =============================================================================
# ABA 3 — ENTRADA (placeholder seguro por enquanto)
# =============================================================================
with abas[2]:
    st.markdown("### ENTRADA")
    st.info("Painel de ENTRADA será ajustado após concluirmos o E-MAIL. (Placeholder seguro.)")
    st.markdown("---")


# =============================================================================
# ABA 4 — SAÍDA (placeholder seguro por enquanto)
# =============================================================================
with abas[3]:
    st.markdown("### SAÍDA")
    st.info("Painel de SAÍDA será ajustado após concluirmos o E-MAIL. (Placeholder seguro.)")
    st.markdown("---")
