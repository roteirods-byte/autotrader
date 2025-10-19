# arquivo: aplicativo.py
# Streamlit 1.33+ (usa st.rerun)

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.headerregistry import Address

import streamlit as st

# =========================
# Config da página
# =========================
st.set_page_config(page_title="Autotrader — Painéis", page_icon="📊", layout="wide")

# =========================
# CSS Global (tema + medidas)
# =========================
ORANGE = "#ff7b1b"
DARK_BG = "#0d2433"
DARK_CARD = "#102a3d"
TEXT_LIGHT = "#e7eef4"

st.markdown(
    f"""
    <style>
    .stApp {{ background: {DARK_BG} !important; }}
    section.main > div.block-container {{
        padding-top: 2rem; padding-bottom: 2rem; color: {TEXT_LIGHT};
    }}
    .aut_title h1 {{ color:{ORANGE}!important; font-weight:800; letter-spacing:.5px; margin-bottom:1rem; }}
    .aut_hr {{ height:1px; background:rgba(255,255,255,.08); margin:.6rem 0 1.4rem 0; }}

    /* Abas */
    div[data-baseweb="tab-list"] button[role="tab"] {{
        color:{ORANGE}!important; border-radius:10px 10px 0 0!important;
        background:transparent!important; border:1px solid rgba(255,255,255,.08)!important; border-bottom:none!important;
    }}
    div[data-baseweb="tab-list"] button[aria-selected="true"] {{
        color:{DARK_BG}!important; background:{ORANGE}!important;
    }}

    /* Inputs dark */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stNumberInput > div > div > input {{
        background:{DARK_CARD}!important; color:{TEXT_LIGHT}!important;
        border-radius:10px!important; border:1px solid rgba(255,255,255,.08)!important;
    }}

    /* 250px de largura e gap 50px */
    .aut .stTextInput > div > div > input {{ width:250px!important; }}
    .aut .stButton > button {{
        background:{ORANGE}!important; color:{DARK_BG}!important; border:none!important;
        border-radius:10px!important; font-weight:700!important; width:250px!important; height:40px!important;
    }}
    .aut .email-row {{ display:flex; align-items:center; gap:50px; flex-wrap:wrap; margin:.5rem 0 .6rem 0; }}
    .aut .field-label {{ color:{ORANGE}; font-weight:700; font-size:.9rem; margin-bottom:.25rem; }}

    .aut .inline-feedback {{ min-width:320px; }}
    .aut .success-box {{ background:#def6e5; color:#104c1f; padding:10px 14px; border-radius:8px; border:1px solid #b6e2bf; }}
    .aut .error-box   {{ background:#fde3e3; color:#8a1a1a; padding:10px 14px; border-radius:8px; border:1px solid #f3b1b1; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Utilitários — e-mail
# =========================
def send_test_email(sender: str, app_password: str, to_addr: str) -> None:
    msg = MIMEText("Teste de e-mail do painel Autotrader — OK ✅", "plain", "utf-8")
    msg["Subject"] = "Autotrader — Teste de E-mail"
    user, dom = sender.split("@", 1)
    msg["From"] = str(Address(display_name="Autotrader", username=user, domain=dom))
    msg["To"] = to_addr

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, app_password)
        server.send_message(msg)

def getenv(key: str, default: str = "") -> str:
    return os.environ.get(key, default)

def set_runtime_env(key: str, value: str) -> None:
    os.environ[key] = value  # mantém durante a sessão

# =========================
# Cabeçalho
# =========================
st.markdown('<div class="aut aut_title"><h1>PAINÉIS DA AUTOMAÇÃO</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="aut aut_hr"></div>', unsafe_allow_html=True)

# =========================
# Abas
# =========================
tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# =============== E-MAIL ===============
with tab_email:
    st.markdown('<div class="aut">', unsafe_allow_html=True)
    st.markdown(f"### <span style='color:{ORANGE};'>E-MAIL</span>", unsafe_allow_html=True)
    st.markdown('<div class="aut_hr"></div>', unsafe_allow_html=True)

    default_user = getenv("MAIL_USER", "")
    default_pass = getenv("MAIL_APP_PASSWORD", "")
    default_to   = getenv("MAIL_TO", "")

    if "email_feedback" not in st.session_state:
        st.session_state.email_feedback = ("", "success")  # (mensagem, tipo)

    st.markdown('<div class="email-row">', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="field-label">Principal:</div>', unsafe_allow_html=True)
        user = st.text_input("Principal", value=default_user, key="email_user",
                             label_visibility="collapsed", placeholder="seuemail@gmail.com")

    with st.container():
        st.markdown('<div class="field-label">Senha:</div>', unsafe_allow_html=True)
        app_password = st.text_input("Senha", value=default_pass, key="email_pass",
                                     type="password", label_visibility="collapsed",
                                     placeholder="Senha de app (Gmail)")

    with st.container():
        st.markdown('<div class="field-label">Envio:</div>', unsafe_allow_html=True)
        to_addr = st.text_input("Envio", value=default_to, key="email_to",
                                label_visibility="collapsed", placeholder="destinatario@dominio.com")

    with st.container():
        st.markdown('<div class="field-label" style="visibility:hidden;">.</div>', unsafe_allow_html=True)
        clicked = st.button("TESTAR/SALVAR", key="btn_test_save")

    with st.container():
        st.markdown('<div class="inline-feedback">', unsafe_allow_html=True)
        msg, kind = st.session_state.email_feedback
        if msg:
            box = "success-box" if kind == "success" else "error-box"
            st.markdown(f'<div class="{box}">{msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # fecha .email-row

    if clicked:
        try:
            if not user or "@" not in user:
                raise ValueError("Informe um e-mail de remetente válido (Gmail).")
            if not app_password:
                raise ValueError("Informe a senha de app do Gmail (App Password).")
            if not to_addr or "@" not in to_addr:
                raise ValueError("Informe um e-mail de destino válido.")
            # Envio
            send_test_email(user, app_password, to_addr)
            # Atualiza ambiente em runtime para a sessão
            set_runtime_env("MAIL_USER", user)
            set_runtime_env("MAIL_APP_PASSWORD", app_password)
            set_runtime_env("MAIL_TO", to_addr)
            st.session_state.email_feedback = ("Configuração salva e e-mail de teste enviado ✅", "success")
            st.rerun()
        except Exception as exc:
            st.session_state.email_feedback = (f"Falha ao salvar/testar e-mail: {str(exc)}", "error")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =============== PLACEHOLDERS ===============
with tab_moedas:
    st.info("Aqui virá o painel **MOEDAS** (aplicaremos o mesmo visual após sua aprovação do E-MAIL).")
with tab_entrada:
    st.info("Aqui virá o painel **ENTRADA**.")
with tab_saida:
    st.info("Aqui virá o painel **SAÍDA**.")
