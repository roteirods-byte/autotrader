# ============================================
# aplicativo.py  —  Automação Cripto (E-mail fix + UI)
# ============================================

# 1) Precisa ser o PRIMEIRO comando do script
import streamlit as st
st.set_page_config(page_title="Automação Cripto", layout="wide")

# 2) Imports padrão
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo  # stdlib (Python 3.9+)

# 3) CSS: encolher inputs (~70%), títulos laranja, abas laranja
SHRINK_CSS = """
<style>
:root { --accent-oran:#ff7a00; }

/* Títulos em laranja */
h1, h2, h3, .st-emotion-cache-10trblm, .stMarkdown strong {
  color: var(--accent-oran) !important;
}

/* Abas em laranja (texto) */
.stTabs [data-baseweb="tab"] p {
  color: var(--accent-oran) !important;
  font-weight: 600;
}

/* Encolher inputs padrão (texto/senha) para ~320px */
div[data-baseweb="input"] > div { max-width: 320px !important; }
div[data-baseweb="input-password"] > div { max-width: 320px !important; }

/* Botão do tamanho do conteúdo */
.stButton > button {
  width: auto !important;
  padding: 0.45rem 1.0rem;
}

/* Realce leve nos blocos de feedback */
.ok-box {
  background: #143d23;
  border: 1px solid #1f6f3a;
  color: #e8ffe8;
  padding: .6rem .8rem;
  border-radius: .4rem;
}
.warn-box {
  background: #3e2a00;
  border: 1px solid #7a4f00;
  color: #ffe6bf;
  padding: .6rem .8rem;
  border-radius: .4rem;
}
</style>
"""
st.markdown(SHRINK_CSS, unsafe_allow_html=True)

# 4) Utilitários

def local_now_str() -> str:
    """Retorna string com horário local, respeitando TZ (padrão America/Sao_Paulo)."""
    tz_name = os.environ.get("TZ", "America/Sao_Paulo")
    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        # Fallback: UTC se TZ inválido
        tz_name = "UTC"
        now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name})"

def send_mail_v2(user: str, app_pass: str, recipients: list[str], subject: str, body: str):
    """Envia e-mail via Gmail/SSL 465."""
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(recipients)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, app_pass)
        server.sendmail(user, recipients, msg.as_string())

# 5) Seção E-MAIL — com inputs menores, horário BR e destino correto
def secao_email():
    st.subheader("Configurações de e-mail")

    # Recupera sessão
    mail_user = st.session_state.get("mail_user", "")
    app_pass  = st.session_state.get("app_pass", "")
    mail_to   = st.session_state.get("mail_to", "")

    col1, col2 = st.columns([1,1])
    with col1:
        mail_user = st.text_input(
            "Principal", value=mail_user,
            placeholder="seu.email@gmail.com", key="mail_user_in"
        )
        app_pass  = st.text_input(
            "Senha (app password)", value=app_pass, type="password",
            key="app_pass_in"
        )
    with col2:
        mail_to   = st.text_input(
            "Envio (opcional)", value=mail_to,
            placeholder="destino@dominio.com (ou vários, separados por vírgula)",
            key="mail_to_in",
            help="Aperte Enter para aplicar; aceita vários separados por vírgula."
        )

    if st.button("ENVIAR / SALVAR", type="primary"):
        # Salva
        st.session_state.mail_user = mail_user.strip()
        st.session_state.app_pass  = app_pass.strip()
        st.session_state.mail_to   = mail_to.strip()

        st.markdown('<div class="ok-box">✅ Dados de e-mail armazenados na sessão.</div>', unsafe_allow_html=True)

        # Monta lista de destinatários:
        # Se 'Envio (opcional)' estiver preenchido => manda SÓ para ele(s).
        # Se vazio => manda para o Principal.
        recipients = [e.strip() for e in st.session_state.mail_to.split(",") if e.strip()]
        if not recipients:
            recipients = [st.session_state.mail_user]

        subject = "Teste - Automação Cripto"
        body = f"E-mail de teste enviado pela Automação Cripto.\nHorário: {local_now_str()}"

        try:
            send_mail_v2(st.session_state.mail_user, st.session_state.app_pass, recipients, subject, body)
            st.markdown(
                f'<div class="ok-box">📧 E-mail de teste enviado via SSL 465 para: <b>{", ".join(recipients)}</b>.</div>',
                unsafe_allow_html=True
            )
            st.caption("Se não aparecer, verifique também a caixa Lixo/Spam (Hotmail/Outlook costuma segurar testes).")
        except Exception as e:
            st.error("Falha ao enviar e-mail.")
            with st.expander("Detalhes técnicos"):
                st.exception(e)

    st.caption("Dica: para Gmail é obrigatório usar App Password (senha de app). "
               "Conta ➜ Segurança ➜ Verificação em duas etapas ➜ Senhas de app.")

# 6) Placeholders das outras abas (não quebram o app; depois integramos)
def secao_moedas():
    st.subheader("Moedas / Pares / Filtros / Pesos")
    st.info("Esta seção será ajustada depois que finalizarmos o painel de E-mail.")

def secao_entrada():
    st.subheader("Regras de Entrada")
    st.info("Esta seção será ajustada depois que finalizarmos o painel de E-mail.")

def secao_saida():
    st.subheader("Monitoramento de Saída")
    st.info("Esta seção será ajustada depois que finalizarmos o painel de E-mail.")

def secao_estado():
    st.subheader("Estado")
    st.info("Esta seção será ajustada depois que finalizarmos o painel de E-mail.")

# 7) Layout principal
def main():
    st.markdown("### Interface do projeto — layout aprovado")
    tabs = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

    with tabs[0]:
        secao_email()
    with tabs[1]:
        secao_moedas()
    with tabs[2]:
        secao_entrada()
    with tabs[3]:
        secao_saida()
    with tabs[4]:
        secao_estado()

if __name__ == "__main__":
    main()
