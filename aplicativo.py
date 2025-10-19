# autotrader/aplicativo.py
from __future__ import annotations

import os
import smtplib
import email.message as em
from typing import Optional

import streamlit as st


# -----------------------------
# Configuração básica da página
# -----------------------------
st.set_page_config(
    page_title="Autotrader — Painéis",
    page_icon="📈",
    layout="wide",
)

# -----------------------------
# CSS GLOBAL (tema / layout)
# -----------------------------
ORANGE = "#ff7b1b"  # cor laranja padrão do projeto

CSS = f"""
<style>
/* Reset leve para ficar consistente */
:root {{
  --orange: {ORANGE};
}}

html, body, [data-testid="stAppViewContainer"] {{
  background-color: #0b2533;  /* fundo azul escuro */
  color: #e7edf3;             /* texto claro */
}}

h1, h2, h3, h4, h5, h6 {{
  color: var(--orange) !important;
  font-weight: 800;
  letter-spacing: .3px;
}}

/* Título grande da página */
h1.page-title {{
  font-size: 34px;
  margin: 8px 0 18px 0;
}}

/* Linha fina separadora */
.hr-thin {{
  height: 1px;
  background: rgba(255,255,255,.12);
  margin: 6px 0 16px 0;
  border-radius: 1px;
}}

/* Abas do Streamlit */
.stTabs [data-baseweb="tab"] {{
  background: transparent;
  border: 1px solid rgba(255,255,255,.10);
  color: #d2dbe2;
  margin-right: 10px;
  border-radius: 6px 6px 0 0;
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
  color: #0b2533;
  background: var(--orange);
  border-color: var(--orange);
}}
.stTabs [data-baseweb="tab"]:hover {{
  border-color: var(--orange);
}}

/* Inputs com 250px e espaçamento de 50px entre eles */
.form-row {{
  display: flex;
  align-items: center;
  gap: 50px; /* espaço entre campos */
  flex-wrap: wrap;
  margin-bottom: 14px;
}}
.form-col {{
  width: 250px; /* largura fixa */
}}
.form-col .stTextInput>div>div>input,
.form-col .stTextInput input {{
  width: 250px !important;
}}
.form-col .stPassword>div>div>input,
.form-col .stPassword input {{
  width: 250px !important;
}}

/* Botão TESTAR/SALVAR com 250px */
.action-col {{
  width: 250px;
}}
.action-col .stButton>button {{
  width: 250px;
  background: var(--orange);
  color: #0b2533;
  border: none;
  font-weight: 700;
  letter-spacing: .5px;
}}
.action-col .stButton>button:hover {{
  filter: brightness(0.95);
}}

/* Mensagem de status, alinhada à direita do botão */
.status-col {{
  flex: 1 1 auto; /* ocupa o resto da linha */
  min-width: 260px;
}}
.status-ok {{
  background: rgba(46, 204, 113, .12);
  color: #a9f5c9;
  border: 1px solid rgba(46, 204, 113, .35);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
}}
.status-err {{
  background: rgba(231, 76, 60, .12);
  color: #ffb5ad;
  border: 1px solid rgba(231, 76, 60, .35);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
}}

/* Rótulos laranja ao lado dos inputs */
.label {{
  color: var(--orange);
  font-weight: 700;
  margin-bottom: 4px;
}}

/* Caixa ”seção” com recuo */
.section {{
  margin-top: 8px;
  margin-bottom: 8px;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -----------------------------
# Utilitário: enviar email
# -----------------------------
def send_test_mail(
    user: str,
    app_password: str,
    to_addr: str,
    subject: str = "Teste de envio — Autotrader",
    body: str = "Mensagem de teste enviada pelo painel Autotrader.",
) -> Optional[str]:
    """
    Envia um e-mail de teste via Gmail (porta 587, TLS).
    Retorna None em caso de sucesso; string de erro em falha.
    """
    try:
        msg = em.Message()
        msg["From"] = user
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_payload(body)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, app_password)
            smtp.sendmail(user, [to_addr], msg.as_string())

        return None
    except Exception as exc:  # noqa: BLE001
        return str(exc)


# -----------------------------
# Valores padrão a partir do ambiente (Render)
# -----------------------------
ENV_DEFAULTS = {
    "MAIL_USER": os.getenv("MAIL_USER", ""),
    "MAIL_APP_PASSWORD": os.getenv("MAIL_APP_PASSWORD", ""),
    "MAIL_TO": os.getenv("MAIL_TO", ""),
}

# Carrega para session_state uma vez
for key, default in (
    ("mail_user", ENV_DEFAULTS["MAIL_USER"]),
    ("mail_pass", ENV_DEFAULTS["MAIL_APP_PASSWORD"]),
    ("mail_to", ENV_DEFAULTS["MAIL_TO"]),
):
    if key not in st.session_state:
        st.session_state[key] = default


# -----------------------------
# Cabeçalho
# -----------------------------
st.markdown('<h1 class="page-title">PAINÉIS DA AUTOMAÇÃO</h1>', unsafe_allow_html=True)
st.markdown('<div class="hr-thin"></div>', unsafe_allow_html=True)

# -----------------------------
# Abas
# -----------------------------
tabs = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# =============================
# 1) ABA E-MAIL
# =============================
with tabs[0]:
    st.markdown("## CORREIO ELETRÔNICO")
    st.markdown('<div class="section"></div>', unsafe_allow_html=True)

    # Linha 1 — Principal / Senha / Envio
    with st.container():
        st.markdown('<div class="form-row">', unsafe_allow_html=True)

        # Principal
        st.markdown('<div class="form-col">', unsafe_allow_html=True)
        st.markdown('<div class="label">Principal:</div>', unsafe_allow_html=True)
        mail_user = st.text_input(
            label="Principal",
            label_visibility="collapsed",
            key="mail_user",
            placeholder="seuemail@gmail.com",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Senha (App Password)
        st.markdown('<div class="form-col">', unsafe_allow_html=True)
        st.markdown('<div class="label">Senha:</div>', unsafe_allow_html=True)
        mail_pass = st.text_input(
            label="Senha",
            label_visibility="collapsed",
            key="mail_pass",
            type="password",
            placeholder="App Password do Gmail",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Envio (destinatário)
        st.markdown('<div class="form-col">', unsafe_allow_html=True)
        st.markdown('<div class="label">Envio:</div>', unsafe_allow_html=True)
        mail_to = st.text_input(
            label="Envio",
            label_visibility="collapsed",
            key="mail_to",
            placeholder="destinatario@exemplo.com",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Botão + Status (mesma linha)
        st.markdown('<div class="action-col">', unsafe_allow_html=True)
        do_test = st.button("TESTAR/SALVAR", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Placeholder para status (fica à direita do botão)
        status_ph = st.empty()

        st.markdown("</div>", unsafe_allow_html=True)

    # Ação do botão
    if do_test:
        # Validação simples
        if not mail_user or not mail_pass or not mail_to:
            status_ph.markdown(
                '<div class="status-err">Preencha todos os campos para testar.</div>',
                unsafe_allow_html=True,
            )
        else:
            err = send_test_mail(mail_user, mail_pass, mail_to)
            if err is None:
                status_ph.markdown(
                    '<div class="status-ok">Configuração salva e e-mail de teste enviado ✅</div>',
                    unsafe_allow_html=True,
                )
            else:
                status_ph.markdown(
                    f'<div class="status-err">Falha ao enviar e-mail: {err}</div>',
                    unsafe_allow_html=True,
                )

# =============================
# 2) ABA MOEDAS (placeholder)
# =============================
with tabs[1]:
    st.markdown("## MOEDAS")
    st.info("Vamos estilizar esta aba depois do e-mail, conforme seu modelo.")

# =============================
# 3) ABA ENTRADA (placeholder)
# =============================
with tabs[2]:
    st.markdown("## ENTRADA")
    st.info("Conteúdo será adicionado na próxima etapa.")

# =============================
# 4) ABA SAÍDA (placeholder)
# =============================
with tabs[3]:
    st.markdown("## SAÍDA")
    st.info("Conteúdo será adicionado na próxima etapa.")
