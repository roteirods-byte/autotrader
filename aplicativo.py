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
    ORANGE = "#ff9a1a"
    st.markdown(
        f"""
        <style>
        /* Fundo geral */
        .stApp {{ background:#0b1f2f; }}

        /* Título principal */
        .app-title h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            color: {ORANGE};
            margin: 0 0 .4rem 0;
        }}
        .app-subtitle {{ border-top:2px solid rgba(255,154,26,.25); margin-bottom:1rem; }}

        /* Abas (orelhinhas) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 40px;
            border-radius: 10px 10px 0 0;
            background:#0e2740;
            border:1px solid rgba(255,255,255,.08);
            color:{ORANGE};                      /* texto laranja nas abas */
            font-weight:700;
        }}
        .stTabs [aria-selected="true"] {{
            background:#123050 !important;
            color:{ORANGE} !important;           /* manter laranja também na aba ativa */
            border-bottom-color:#123050 !important;
        }}

        /* Painel “cartão” */
        .panel {{
            background:#0e2740;
            border:1px solid rgba(255,255,255,.08);
            border-radius:12px;
            padding:14px;
            box-shadow:0 8px 30px rgba(0,0,0,.20);
        }}

        /* Rótulos em linha */
        .inline-label {{
            color:{ORANGE};
            font-weight:800;
            letter-spacing:.2px;
            margin:.2rem 0 .25rem 0;
            white-space:nowrap;
        }}

        /* Linha flex para controlar larguras/gaps */
        .inline-row {{
            display:flex;
            align-items:flex-end;
            flex-wrap:wrap;
            gap:50px;                             /* 3) gap de 50px entre as caixas */
        }}

        /* Caixas com largura fixa de 250px */
        .inline-row .unit {{ width:250px; }}
        .inline-row .unit input {{
            width:250px !important;               /* 2) inputs 250px */
            height:42px;
            background:#0b2236;
            color:#e8eef5;
            border:1px solid rgba(255,255,255,.12);
            border-radius:10px;
        }}
        .inline-row .unit input::placeholder {{ color:#7da0bd; opacity:.75; }}

        /* Botão com o mesmo tamanho e alinhamento */
        .inline-row .unit-btn button {{
            width:250px;                          /* 4) mesmo tamanho dos inputs */
            height:42px;
            border-radius:10px;
            font-weight:800;
            letter-spacing:.3px;
            background:{ORANGE};                  /* 1) botão laranja */
            color:#0b1f2f;
            border:1px solid rgba(255,255,255,.12);
        }}
        .inline-row .unit-btn button:hover {{ filter:brightness(1.05); }}

        /* Mensagem de confirmação alinhada à direita do botão */
        .inline-row .unit-msg {{
            min-width: 280px;
            color:#d8f3dc;
        }}

        /* Esconder eventuais mensagens auxiliares/resíduos de formulários */
        .stForm, .stCaption {{ display:none !important; }}
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
# UI — Painel E-MAIL
# =========================
def render_email_panel() -> None:
    cfg = _load_email_config()
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    # Cabeçalho do painel
    st.markdown('<div class="inline-label" style="font-size:1rem;">E-MAIL</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border-color:rgba(255,255,255,.12);" />', unsafe_allow_html=True)

    # Linha com campos + botão + mensagem
    msg_placeholder = st.empty()  # manter referência para mostrar mensagem no final (fallback)

    # Construímos a linha manualmente para garantir 250px + gap 50px
    # Cada "unit" tem 250px; gap entre elas é controlado por CSS (.inline-row)
    st.markdown('<div class="inline-row">', unsafe_allow_html=True)

    # Principal
    col_html = """
        <div class="unit">
            <div class="inline-label">Principal:</div>
        </div>
    """
    st.markdown(col_html, unsafe_allow_html=True)
    principal = st.text_input("principal_hidden", value=cfg["principal"], placeholder="seuemail@gmail.com", label_visibility="hidden", key="email_principal")

    # Senha
    st.markdown('<div class="unit"><div class="inline-label">Senha:</div></div>', unsafe_allow_html=True)
    app_password = st.text_input("senha_hidden", value=cfg["app_password"], placeholder="senha de app", type="password", label_visibility="hidden", key="email_senha")

    # Envio
    st.markdown('<div class="unit"><div class="inline-label">Envio:</div></div>', unsafe_allow_html=True)
    enviar_para = st.text_input("envio_hidden", value=cfg["enviar_para"], placeholder="destinatario@provedor.com", label_visibility="hidden", key="email_envio")

    # Botão
    st.markdown('<div class="unit unit-btn">', unsafe_allow_html=True)
    salvar = st.button("TESTAR/SALVAR", key="btn_testar_salvar")
    st.markdown("</div>", unsafe_allow_html=True)

    # Espaço onde exibimos a confirmação alinhada à direita do botão
    st.markdown('<div class="unit unit-msg" id="email_msg_slot"></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # fecha inline-row
    st.markdown("</div>", unsafe_allow_html=True)  # fecha panel

    if salvar:
        if not principal or not app_password or not enviar_para:
            st.markdown(
                "<script>document.getElementById('email_msg_slot').innerHTML="
                "'<span style=\"color:#ffd166;\">⚠️ Preencha Principal, Senha e Envio.</span>';</script>",
                unsafe_allow_html=True,
            )
        else:
            try:
                _save_email_config(principal, app_password, enviar_para)
                _send_test_email(principal, app_password, enviar_para)
                st.markdown(
                    "<script>document.getElementById('email_msg_slot').innerHTML="
                    "'<span style=\"color:#8be28b;\">✅ Configuração salva e e-mail de teste enviado.</span>';</script>",
                    unsafe_allow_html=True,
                )
            except Exception as exc:  # noqa: BLE001
                st.markdown(
                    "<script>document.getElementById('email_msg_slot').innerHTML="
                    f"'<span style=\"color:#ff7b7b;\">❌ Falha ao salvar/testar e-mail: {str(exc).replace(\"'\",\"&#39;\")}</span>';</script>",
                    unsafe_allow_html=True,
                )


# =========================
# App
# =========================
def main() -> None:
    st.set_page_config(page_title="Autotrader — Painéis", layout="wide")
    inject_css()
    _ensure_email_table()

    # Título
    st.markdown('<div class="app-title"><h1>PAINÉIS DA AUTOMAÇÃO</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle"></div>', unsafe_allow_html=True)

    # Abas com nomes no padrão
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
