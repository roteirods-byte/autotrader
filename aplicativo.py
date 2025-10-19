# autotrader/aplicativo.py
from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from typing import Dict

import psycopg2
import streamlit as st


# =========================
# Infra: DB (Postgres)
# =========================
def _get_conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        st.error("DATABASE_URL não configurado no serviço Web (Render → Ambiente).")
        st.stop()
    return psycopg2.connect(url)


def _ensure_email_table() -> None:
    """Cria a tabela de config de e-mail, se não existir."""
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS email_config (
                id           SERIAL PRIMARY KEY,
                principal    TEXT NOT NULL,
                app_password TEXT NOT NULL,
                enviar_para  TEXT NOT NULL,
                updated_at   TIMESTAMPTZ DEFAULT now()
            );
            """
        )
        conn.commit()


def _load_email_config() -> Dict[str, str]:
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT principal, app_password, enviar_para FROM email_config WHERE id=1;"
        )
        row = cur.fetchone()
        if row:
            return {
                "principal": row[0] or "",
                "app_password": row[1] or "",
                "enviar_para": row[2] or "",
            }
    # default vazio
    return {"principal": "", "app_password": "", "enviar_para": ""}


def _save_email_config(principal: str, app_password: str, enviar_para: str) -> None:
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM email_config WHERE id=1;")
        if cur.fetchone():
            cur.execute(
                """
                UPDATE email_config
                   SET principal=%s,
                       app_password=%s,
                       enviar_para=%s,
                       updated_at=now()
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


# =========================
# E-mail: envio de teste
# =========================
def _send_test_email(principal: str, app_password: str, enviar_para: str) -> None:
    """
    Envia e-mail de teste via Gmail (App Password).
    Para outro provedor, ajuste host/porta abaixo.
    """
    msg = MIMEText("Teste ok: painel E-MAIL configurado com sucesso ✅")
    msg["Subject"] = "Autotrader - Teste de e-mail"
    msg["From"] = principal
    msg["To"] = enviar_para

    # Gmail via SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(principal, app_password)
        smtp.send_message(msg)


# =========================
# UI: Painéis
# =========================
def render_email_panel() -> None:
    st.subheader("E-MAIL")

    cfg = _load_email_config()

    with st.form("email_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([2.4, 2.2, 2.6])

        with col1:
            principal = st.text_input(
                "Principal (remetente):",
                value=cfg["principal"],
                placeholder="seuemail@gmail.com",
            )

        with col2:
            app_password = st.text_input(
                "Senha (App Password):", value=cfg["app_password"], type="password"
            )
            st.caption("Use **senha de app** do seu e-mail (não a senha normal).")

        with col3:
            enviar_para = st.text_input(
                "Envio (destinatário):",
                value=cfg["enviar_para"],
                placeholder="destinatario@provedor.com",
            )

        salvar = st.form_submit_button("TESTAR/SALVAR", use_container_width=True)

    if salvar:
        if not principal or not app_password or not enviar_para:
            st.error("Preencha Principal, App Password e Envio.")
            return
        try:
            _save_email_config(principal, app_password, enviar_para)
            _send_test_email(principal, app_password, enviar_para)
            st.success("Configuração salva e e-mail de teste enviado ✅")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Falha ao salvar/testar e-mail: {exc}")


def main() -> None:
    st.set_page_config(page_title="Autotrader", layout="wide")
    st.title("Autotrader — Painéis")

    # Cria tabela necessária
    _ensure_email_table()

    tabs = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])
    with tabs[0]:
        render_email_panel()
    with tabs[1]:
        st.info("Painel MOEDAS — em breve.")
    with tabs[2]:
        st.info("Painel ENTRADA — em breve.")
    with tabs[3]:
        st.info("Painel SAÍDA — em breve.")


if __name__ == "__main__":
    main()
