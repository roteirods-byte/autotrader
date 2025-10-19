# autotrader/aplicativo.py
from __future__ import annotations

import os
import smtplib
import email.message as em
from typing import Optional

import streamlit as st


# =============================
# Config da página
# =============================
st.set_page_config(page_title="Autotrader — Painéis", page_icon="📈", layout="wide")

ORANGE = "#ff7b1b"

CSS = f"""
<style>
:root {{
  --orange: {ORANGE};
  --bg: #0b2533;
  --text: #e7edf3;
}}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg);
  color: var(--text);
}}

h1, h2, h3, h4, h5, h6 {{
  color: var(--orange) !important;
  font-weight: 800;
  letter-spacing: .3px;
}}
h1.page-title {{ font-size: 34px; margin: 8px 0 18px 0; }}
.hr-thin {{ height:1px; background: rgba(255,255,255,.12); margin: 6px 0 16px; }}

/* Abas (“orelhas”) SEMPRE com nomes em laranja */
.stTabs div[role="tablist"] > div[role="tab"] {{
  background: transparent;
  border: 1px solid rgba(255,255,255,.10);
  margin-right: 10px;
  border-radius: 6px 6px 0 0;
}}
.stTabs div[role="tablist"] > div[role="tab"] p {{
  color: var(--orange) !important;  /* nomes laranja permanentemente */
  margin: 0;
}}
/* Aba ativa: realce leve para manter legibilidade do texto laranja */
.stTabs div[role="tablist"] > div[role="tab"][aria-selected="true"] {{
  background: rgba(255,123,27,.18);
  border-color: var(--orange);
}}
.stTabs div[role="tablist"] > div[role="tab"]:hover {{
  border-color: var(--orange);
}}

/* ======== CONTROLES: 250px + gap 50px ======== */
div[data-testid="stTextInput"],
div[data-testid="stPassword"] {{
  width: 250px !important;
  display: inline-block !important;
  vertical-align: top;
  margin-right: 50px;     /* gap entre campos */
}}
div[data-testid="stTextInput"] input,
div[data-testid="stPassword"] input {{
  width: 250px !important;
}}

/* Botão 250px */
div[data-testid="stButton"] > button {{
  width: 250px !important;
  background: var(--orange);
  color: var(--bg);
  border: none;
  font-weight: 700;
  letter-spacing: .5px;
}}
div[data-testid="stButton"] {{
  display: inline-block !important;
  vertical-align: top;
  margin-right: 50px;
}}
div[data-testid="stButton"] > button:disabled {{
  opacity: .65;
  background: var(--orange);
  color: var(--bg);
}}

/* Mensagens ao lado do botão */
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
.label {{ color: var(--orange); font-weight:700; margin: 6px 0 4px; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# =============================
# Envio de e-mail (Gmail TLS)
# =============================
def send_test_mail(
    user: str,
    app_password: str,
    to_addr: str,
    subject: str = "Teste de envio — Autotrader",
    body: str = "Mensagem de teste enviada pelo painel Autotrader.",
) -> Optional[str]:
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


# =============================
# Defaults (Render)
# =============================
defaults = {
    "mail_user": os.getenv("MAIL_USER", ""),
    "mail_pass": os.getenv("MAIL_APP_PASSWORD", ""),
    "mail_to": os.getenv("MAIL_TO", ""),
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

st.session_state.setdefault("status_msg", "")
st.session_state.setdefault("status_cls", "")


# =============================
# Cabeçalho + Abas
# =============================
st.markdown('<h1 class="page-title">PAINÉIS DA AUTOMAÇÃO</h1>', unsafe_allow_html=True)
st.markdown('<div class="hr-thin"></div>', unsafe_allow_html=True)

tabs = st.tabs(["CORREIO ELETRÔNICO", "MOEDAS", "ENTRADA", "SAÍDA"])

# =============================
# 1) E-MAIL
# =============================
with tabs[0]:
    st.markdown("## CORREIO ELETRÔNICO")

    # Mesma LINHA: 3 campos + botão + status
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 2.2])

    with c1:
        st.markdown('<div class="label">Principal:</div>', unsafe_allow_html=True)
        mail_user = st.text_input("Principal", key="mail_user", label_visibility="collapsed")

    with c2:
        st.markdown('<div class="label">Senha:</div>', unsafe_allow_html=True)
        mail_pass = st.text_input("Senha", type="password", key="mail_pass", label_visibility="collapsed")

    with c3:
        st.markdown('<div class="label">Envio:</div>', unsafe_allow_html=True)
        mail_to = st.text_input("Envio", key="mail_to", label_visibility="collapsed")

    with c4:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)  # alinhar top
        send_now = st.button("TESTAR/SALVAR")

    with c5:
        status_placeholder = st.empty()

    # Exibir status anterior (persistência leve)
    if st.session_state["status_msg"]:
        status_placeholder.markdown(
            f'<div class="{st.session_state["status_cls"]}">{st.session_state["status_msg"]}</div>',
            unsafe_allow_html=True,
        )

    # Clique no botão
    if send_now:
        if not mail_user or not mail_pass or not mail_to:
            st.session_state["status_msg"] = "Preencha todos os campos para testar."
            st.session_state["status_cls"] = "status-err"
        else:
            err = send_test_mail(mail_user, mail_pass, mail_to)
            if err is None:
                st.session_state["status_msg"] = "Configuração salva e e-mail de teste enviado ✅"
                st.session_state["status_cls"] = "status-ok"
            else:
                st.session_state["status_msg"] = f"Falha ao enviar e-mail: {err}"
                st.session_state["status_cls"] = "status-err"

        status_placeholder.markdown(
            f'<div class="{st.session_state["status_cls"]}">{st.session_state["status_msg"]}</div>',
            unsafe_allow_html=True,
        )

# =============================
# 2) MOEDAS (placeholder)
# =============================
with tabs[1]:
    st.markdown("## MOEDAS")
    st.info("Vamos estilizar esta aba depois do E-MAIL, seguindo o mesmo padrão.")

# =============================
# 3) ENTRADA (placeholder)
# =============================
with tabs[2]:
    st.markdown("## ENTRADA")
    st.info("Conteúdo será adicionado na próxima etapa.")

# =============================
# 4) SAÍDA (placeholder)
# =============================
with tabs[3]:
    st.markdown("## SAÍDA")
    st.info("Conteúdo será adicionado na próxima etapa.")
