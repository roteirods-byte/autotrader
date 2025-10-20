# panels/email_panel.py — SUBSTITUA INTEIRO
# Streamlit PURO + envio real de e-mail de TESTE (Gmail com senha de app)

import streamlit as st
import smtplib, ssl
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587  # TLS

def _flash_messages():
    ss = st.session_state
    ok = ss.get("email_success") or ss.get("flash_success")
    er = ss.get("email_error") or ss.get("flash_error")
    return ok, er

def _send_test_email(sender: str, app_password: str, to_addr: str) -> None:
    """Envia 1 e-mail de TESTE. Levanta exceção se falhar."""
    msg = EmailMessage()
    msg["Subject"] = "Autotrader — teste de e-mail"
    msg["From"] = sender
    msg["To"] = to_addr
    msg.set_content("Teste de e-mail do Autotrader: sucesso! ✅")

    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ctx)
        smtp.login(sender, app_password)          # senha de app do Gmail
        smtp.send_message(msg)

def render_email_panel() -> None:
    # Mensagens anteriores (se houver)
    ok, er = _flash_messages()
    if ok: st.success(ok, icon="✅")
    if er: st.error(er, icon="⚠️")

    # Formulário: 3 campos + botão
    with st.form("EMAIL_FORM", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns([3,3,3,2], gap="medium")

        with c1:
            sender = st.text_input(
                "Remetente (Gmail)",
                key="sender",
                value=st.session_state.get("sender", st.session_state.get("sender_email", "")),
                placeholder="voce@gmail.com",
            )

        with c2:
            app_password = st.text_input(
                "Senha de app (Gmail)",
                key="app_password",
                value=st.session_state.get("app_password", st.session_state.get("email_app_password", "")),
                type="password",
                placeholder="16 caracteres",
            )

        with c3:
            to_email = st.text_input(
                "Enviar para",
                key="to_email",
                value=st.session_state.get("to_email", st.session_state.get("email_to", "")),
                placeholder="destinatario@dominio.com",
            )

        with c4:
            st.write(""); st.write("")  # alinhamento
            submitted = st.form_submit_button("ENVIAR TESTE")

    # Sinal para outras partes do app (se precisar)
    st.session_state["email_submit"] = submitted
    st.session_state["sender_email"] = sender
    st.session_state["email_app_password"] = app_password
    st.session_state["email_to"] = to_email

    # Ao enviar: tenta mandar o e-mail de teste
    if submitted:
        try:
            if not sender or not app_password or not to_email:
                raise ValueError("Preencha os 3 campos.")

            _send_test_email(sender, app_password, to_email)
            st.session_state["email_success"] = f"E-mail de teste enviado para {to_email}."
            st.session_state["email_error"] = None
            st.success(st.session_state["email_success"], icon="✅")

        except Exception as e:
            msg = str(e)
            # Dicas comuns do Gmail
            if "Invalid credentials" in msg or "Authentication" in msg:
                msg = "Falha de login no Gmail. Use **senha de app** (2FA ligado)."
            elif "Timed out" in msg or "timeout" in msg.lower():
                msg = "Não conectou ao servidor SMTP. Tente novamente."
            st.session_state["email_error"] = msg
            st.session_state["email_success"] = None
            st.error(msg, icon="⚠️")
