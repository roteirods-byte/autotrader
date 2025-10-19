# autotrader/aplicativo.py
from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from typing import Dict

import psycopg2
import streamlit as st


# =========================
# CSS (tema e layout)
# =========================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* Página geral */
        .stApp {
            background: #0b1f2f;               /* navy escuro */
        }
        /* Container central mais “clean” */
        section.main > div {
            padding-top: 1.2rem;
        }

        /* Título principal */
        .app-title h1 {
            font-size: 2.2rem;
            line-height: 1.1;
            font-weight: 800;
            color: #ff9a1a;                   /* laranja */
            margin: 0 0 0.6rem 0;
        }
        .app-subtitle {
            border-top: 2px solid rgba(255,154,26,0.25);
            margin-bottom: 1.2rem;
        }

        /* Cartão/painel */
        .panel {
            background: #0e2740;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 14px 14px 10px 14px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.20);
        }

        /* Rótulos inline (Principal:, Senha:, Envio:) */
        .inline-label {
            color: #ff9a1a;
            font-weight: 800;
            letter-spacing: .2px;
            margin-top: .2rem;
            white-space: nowrap;
        }

        /* Inputs escuros */
        [data-testid="stTextInput"] input {
            background: #0b2236;
            color: #e8eef5;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            height: 42px;
        }
        [data-testid="stTextInput"] input::placeholder {
            color: #7da0bd;
            opacity: .75;
        }

        /* Botão primário */
        .stButton > button {
            height: 44px;
            width: 100%;
            border-radius: 10px;
            font-weight: 800;
            letter-spacing: .3px;
            background: #1e90ff;
            color: #fff;
            border: 1px solid rgba(255,255,255,0.12);
        }
        .stButton > button:hover {
            filter: brightness(1.05);
        }

        /* Remover margens extras de tabs e manter tema escuro */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 10px 10px 0 0;
            background: #0e2740;
            color: #d8e3ef;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .stTabs [aria-selected="true"] {
            background: #123050 !important;
            color: #fff !important;
            border-bottom-color: #123050 !important;
        }

        /* Esconder eventuais dicas intrusivas de formulário (fallback) */
        .stForm, .stCaption { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# DB (Postgres)
# =========================
def _get_conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        st.error("DATABASE_URL não configurado no serviço Web (Render → Ambiente).")
        st.stop()
    return psycopg2.connect(url)


def _ensure_email_table() -> None:
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
            return {"principal": row[0], "app_password": row[1], "enviar_para": row[2]}
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
# E-mail (envio de teste)
# =========================
def _send_test_email(principal: str, app_password: str, enviar_para: str) -> None:
    msg = MIMEText("Teste ok: painel E-MAIL configurado com sucesso ✅")
    msg["Subject"] = "Autotrader - Teste de e-mail"
    msg["From"] = principal
    msg["To"] = enviar_para

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(principal, app_password)
        smtp.send_message(msg)


# =========================
# UI — Painel E-MAIL (modelo)
# =========================
def render_email_panel() -> None:
    cfg = _load_email_config()

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    # linha: rótulo EMAIL
    st.markdown(
        '<div class="inline-label" style="font-size:1rem;margin-bottom:.4rem;">E-MAIL</div>',
        unsafe_allow_html=True,
    )

    # linha com rótulos e campos em linha
    # layout: [lbl1, input1, lbl2, input2, lbl3, input3, botão]
    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.9, 2.6, 0.8, 2.3, 0.8, 2.7, 1.2])

    with c1:
        st.markdown('<div class="inline-label">Principal:</div>', unsafe_allow_html=True)
    with c2:
        principal = st.text_input(
            label="principal_hidden",
            value=cfg["principal"],
            placeholder="seuemail@gmail.com",
            label_visibility="hidden",
        )

    with c3:
        st.markdown('<div class="inline-label">Senha:</div>', unsafe_allow_html=True)
    with c4:
        app_password = st.text_input(
            label="senha_hidden",
            value=cfg["app_password"],
            placeholder="senha de app",
            type="password",
            label_visibility="hidden",
        )

    with c5:
        st.markdown('<div class="inline-label">Envio:</div>', unsafe_allow_html=True)
    with c6:
        enviar_para = st.text_input(
            label="envio_hidden",
            value=cfg["enviar_para"],
            placeholder="destinatario@provedor.com",
            label_visibility="hidden",
        )

    with c7:
        salvar = st.button("TESTAR/SALVAR")

    if salvar:
        if not principal or not app_password or not enviar_para:
            st.toast("Preencha Principal, Senha de App e Envio.", icon="⚠️")
        else:
            try:
                _save_email_config(principal, app_password, enviar_para)
                _send_test_email(principal, app_password, enviar_para)
                st.toast("Configuração salva e e-mail de teste enviado.", icon="✅")
            except Exception as exc:  # noqa: BLE001
                st.toast(f"Falha ao salvar/testar e-mail: {exc}", icon="❌")
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# App
# =========================
def main() -> None:
    st.set_page_config(page_title="Autotrader — Painéis", layout="wide")
    inject_css()
    _ensure_email_table()

    # Título no padrão do projeto
    st.markdown('<div class="app-title"><h1>PAINÉIS DA AUTOMAÇÃO</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle"></div>', unsafe_allow_html=True)

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
