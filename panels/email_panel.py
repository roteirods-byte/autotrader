# autotrader/panels/email_panel.py
from __future__ import annotations
import os
import smtplib
import psycopg2
import streamlit as st
from email.mime.text import MIMEText

def _get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def _load_email_config():
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT principal, app_password, enviar_para FROM email_config WHERE id=1;")
            row = cur.fetchone()
            if row:
                return {"principal": row[0], "app_password": row[1], "enviar_para": row[2]}
            return {"principal": "", "app_password": "", "enviar_para": ""}

def _save_email_config(principal: str, app_password: str, enviar_para: str):
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM email_config WHERE id=1;")
            if cur.fetchone():
                cur.execute(
                    """
                    UPDATE email_config
                       SET principal=%s, app_password=%s, enviar_para=%s, updated_at=now()
                     WHERE id=1;
                    """,
                    (principal, app_password, enviar_para),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO email_config (id, principal, app_password, enviar_para)
                    VALUES (1, %s, %s, %s);
                    """,
                    (principal, app_password, enviar_para),
                )
        conn.commit()

def _send_test_email(principal: str, app_password: str, enviar_para: str):
    msg = MIMEText("Teste ok: painel E-MAIL configurado com sucesso ✅")
    msg["Subject"] = "Autotrader - Teste de e-mail"
    msg["From"] = principal
    msg["To"] = enviar_para

    # Gmail via SSL (senha de App do Gmail)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(principal, app_password)
        smtp.send_message(msg)

def render():
    st.markdown("### E-MAIL")

    cfg = _load_email_config()

    col1, col2, col3, col4 = st.columns([2.4, 2.2, 2.6, 1.2])
    with col1:
        principal = st.text_input("Principal:", value=cfg["principal"], placeholder="seuemail@gmail.com")
    with col2:
        app_password = st.text_input("Senha (App Password):", value=cfg["app_password"], type="password")
    with col3:
        enviar_para = st.text_input("Envio:", value=cfg["enviar_para"], placeholder="destinatario@provedor.com")
    with col4:
        st.write("")  # espaçador
        salvar = st.button("TESTAR/SALVAR", use_container_width=True)

    if salvar:
        if not principal or not app_password or not enviar_para:
            st.error("Preencha Principal, Senha e Envio.")
            return
        try:
            # 1) salva
            _save_email_config(principal, app_password, enviar_para)
            # 2) testa
            _send_test_email(principal, app_password, enviar_para)
            st.success("Configuração salva e e-mail de teste enviado ✅")
        except Exception as exc:
            st.error(f"Falha ao salvar/testar e-mail: {exc}")
