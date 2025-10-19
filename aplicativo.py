# arquivo: aplicativo.py
# Streamlit 1.33+
# Painéis da Automação — layout unificado + painel E-MAIL no padrão solicitado

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.headerregistry import Address

import streamlit as st


# =========================
# Configuração da Página
# =========================
st.set_page_config(
    page_title="Autotrader — Painéis",
    page_icon="📊",
    layout="wide",
)

# =========================
# CSS Global (tema escuro + abóbora + medidas)
# =========================
ORANGE = "#ff7b1b"
DARK_BG = "#0d2433"        # azul-escuro do projeto
DARK_CARD = "#102a3d"      # cartões/inputs
TEXT_LIGHT = "#e7eef4"

st.markdown(
    f"""
    <style>
    /* Tema de fundo */
    .stApp {{
        background: {DARK_BG} !important;
    }}
    /* Container central sem borda branca */
    section.main > div.block-container {{
        padding-top: 2.0rem;
        padding-bottom: 2.0rem;
        color: {TEXT_LIGHT};
    }}

    /* Título principal em abóbora */
    .autotrader-title h1 {{
        color: {ORANGE} !important;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 1.0rem;
    }}

    /* Linha divisória */
    .autotrader-hr {{
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 0.6rem 0 1.4rem 0;
    }}

    /* Tabs (abas) — títulos em abóbora */
    div[data-baseweb="tab-list"] button[role="tab"] {{
        color: {ORANGE} !important;
        border-radius: 10px 10px 0 0 !important;
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-bottom: none !important;
    }}
    div[data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {DARK_BG} !important;
        background: {ORANGE} !important;
    }}

    /* Cards/inputs no tom dark */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {{
        background-color: {DARK_CARD} !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }}

    /* Largura fixa dos inputs (250px) */
    .autotrader .stTextInput > div > div > input {{
        width: 250px !important;
    }}

    /* Botão principal em abóbora, 250px */
    .autotrader .stButton > button {{
        background: {ORANGE} !important;
        color: {DARK_BG} !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        width: 250px !important;
        height: 40px !important;
    }}

    /* Espaçamento horizontal fixo de 50px na linha do formulário */
    .autotrader .email-row {{
        display: flex;
        align-items: center;
        gap: 50px; /* <== EXIGIDO */
        flex-wrap: wrap; /* se ficar apertado em telas pequenas */
        margin-top: 0.5rem;
        margin-bottom: 0.6rem;
    }}

    /* Rótulos em laranja suave */
    .autotrader .field-label {{
        color: {ORANGE};
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }}

    /* Mensagens ao lado do botão (mesma linha) */
    .autotrader .inline-feedback {{
        min-width: 320px;
    }}
    .autotrader .success-box {{
        background: #def6e5;
        color: #104c1f;
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #b6e2bf;
    }}
    .autotrader .error-box {{
        background: #fde3e3;
        color: #8a1a1a;
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #f3b1b1;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Utilitários — e-mail
# =========================
def send_test_email(sender: str, app_password: str, to_addr: str) -> None:
    """
    Envia um e-mail de teste usando SMTP do Gmail (porta 465).
    Lança exceção em caso de erro (capturada no handler do botão).
    """
    # Corpo simples
    msg = MIMEText("Teste de e-mail do painel Autotrader — OK ✅", "plain", "utf-8")
    msg["Subject"] = "Autotrader — Teste de E-mail"
    msg["From"] = str(Address(display_name="Autotrader", username=sender.split("@")[0], domain=sender.split("@")[1]))
    msg["To"] = to_addr

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, app_password)
        server.send_message(msg)


def get_env_default(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def set_runtime_env(key: str, value: str) -> None:
    """
    Ajusta variável de ambiente apenas no runtime atual.
    (Em Render, isso não sobrescreve variáveis persistentes do painel,
     mas mantém a experiência coerente durante a sessão).
    """
    os.environ[key] = value


# =========================
# Cabeçalho
# =========================
st.markdown('<div class="autotrader autotrader-title"><h1>PAINÉIS DA AUTOMAÇÃO</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="autotrader autotrader-hr"></div>', unsafe_allow_html=True)

# =========================
# Abas
# =========================
tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])


# ===========================================================
# ABA: E-MAIL  (no padrão especificado)
# ===========================================================
with tab_email:
    st.markdown('<div class="autotrader">', unsafe_allow_html=True)

    # Seção / título em abóbora
    st.markdown(f"### <span style='color:{ORANGE};'>E-MAIL</span>", unsafe_allow_html=True)
    st.markdown('<div class="autotrader-hr"></div>', unsafe_allow_html=True)

    # Valores padrão vindos do Ambiente (se houver)
    default_user = get_env_default("MAIL_USER", "")
    default_pass = get_env_default("MAIL_APP_PASSWORD", "")
    default_to   = get_env_default("MAIL_TO", "")

    # Estados de sessão para feedback inline
    if "email_feedback" not in st.session_state:
        st.session_state.email_feedback = ("", "success")  # msg, tipo ("success"|"error")

    # Linha dos três campos + botão + feedback (todos com 250 px e gap 50 px)
    st.markdown('<div class="email-row">', unsafe_allow_html=True)

    # Campo: Principal (remetente)
    with st.container():
        st.markdown('<div class="field-label">Principal:</div>', unsafe_allow_html=True)
        user = st.text_input(
            label="Principal",
            value=default_user,
            key="email_user",
            label_visibility="collapsed",
            placeholder="seuemail@gmail.com",
        )

    # Campo: Senha (app password do Gmail)
    with st.container():
        st.markdown('<div class="field-label">Senha:</div>', unsafe_allow_html=True)
        app_password = st.text_input(
            label="Senha",
            value=default_pass,
            key="email_pass",
            type="password",
            label_visibility="collapsed",
            placeholder="Senha de app (Gmail)",
        )

    # Campo: Envio (destinatário)
    with st.container():
        st.markdown('<div class="field-label">Envio:</div>', unsafe_allow_html=True)
        to_addr = st.text_input(
            label="Envio",
            value=default_to,
            key="email_to",
            label_visibility="collapsed",
            placeholder="destinatario@dominio.com",
        )

    # Botão Testar/Salvar
    with st.container():
        st.markdown('<div class="field-label" style="visibility:hidden;">.</div>', unsafe_allow_html=True)
        clicked = st.button("TESTAR/SALVAR", key="btn_test_save")

    # Área do feedback inline (na mesma linha do botão)
    with st.container():
        st.markdown('<div class="inline-feedback">', unsafe_allow_html=True)
        msg, kind = st.session_state.email_feedback
        if msg:
            box_cls = "success-box" if kind == "success" else "error-box"
            st.markdown(f'<div class="{box_cls}">{msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # fecha .email-row

    # Handler do botão
    if clicked:
        try:
            # Validações simples
            if not user or "@" not in user:
                raise ValueError("Informe um e-mail de remetente válido (Gmail).")
            if not app_password:
                raise ValueError("Informe a senha de app do Gmail (App Password).")
            if not to_addr or "@" not in to_addr:
                raise ValueError("Informe um e-mail de destino válido.")

            # Envia e-mail de teste
            send_test_email(user, app_password, to_addr)

            # Atualiza o “runtime env” para manter a experiência
            set_runtime_env("MAIL_USER", user)
            set_runtime_env("MAIL_APP_PASSWORD", app_password)
            set_runtime_env("MAIL_TO", to_addr)

            st.session_state.email_feedback = ("Configuração salva e e-mail de teste enviado ✅", "success")
            st.experimental_rerun()  # atualiza a mensagem na mesma linha

        except Exception as exc:
            # Mensagem amigável, sem HTML complexo (evita erros de escape)
            st.session_state.email_feedback = (f"Falha ao salvar/testar e-mail: {str(exc)}", "error")
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # fecha .autotrader


# ===========================================================
# Demais abas — placeholders (mantemos enquanto você revisa o e-mail)
# ===========================================================
with tab_moedas:
    st.info("Aqui virá o painel **MOEDAS** (vamos aplicar o mesmo visual depois que você aprovar o E-MAIL).")

with tab_entrada:
    st.info("Aqui virá o painel **ENTRADA**.")

with tab_saida:
    st.info("Aqui virá o painel **SAÍDA**.")
