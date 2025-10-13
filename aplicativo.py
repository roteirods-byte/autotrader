# ==============================================
# aplicativo.py  — RESGATE + E-MAIL REVISADO
# ==============================================
import streamlit as st
import ssl, smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------- Fuso horário SP (p/ horário certo no e-mail)
try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    _TZ = None

def _now_sp():
    try:
        return datetime.now(_TZ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------- CONFIGURAÇÃO DA PÁGINA (chamar uma ÚNICA vez e no topo)
st.set_page_config(page_title="Automação Cripto", layout="wide")

# --------- ESTILOS GERAIS
st.markdown("""
<style>
  .orange { color:#ff8c00; font-weight:700; }
  .muted  { opacity:.85; }
  /* inputs mais compactos */
  .email-row .stTextInput > div > div > input {
      padding:6px 10px; font-size:14px; height:38px;
  }
  .email-row .stButton>button { height:40px; font-weight:700; }
  .email-row [data-testid="stTextInput"] { margin-bottom:0.25rem; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# SEÇÃO E-MAIL (revisada — campos em uma linha)
# ==================================================
def _send_test_email(user: str, app_password: str, to_addr: str):
    """Envia e-mail de teste via Gmail (SSL 465)."""
    if not to_addr:
        to_addr = user
    msg = MIMEText(
        f"E-mail de teste enviado pela Automação Cripto.\nHorário: {_now_sp()}"
    )
    msg["Subject"] = "Teste — Automação Cripto"
    msg["From"] = user
    msg["To"] = to_addr

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, app_password)
        server.sendmail(user, [to_addr], msg.as_string())

def secao_email():
    st.subheader("Configurações de e-mail")

    # Valores atuais (mantém os que já estavam na sessão)
    user = st.session_state.get("MAIL_USER", "")
    passwd = st.session_state.get("MAIL_APP_PASSWORD", "")
    to_addr = st.session_state.get("MAIL_TO", "")

    # Três campos + botão, em uma linha
    c1, c2, c3, c4 = st.columns([3, 3, 3, 1.4], gap="small")

    with c1:
        st.markdown("<div class='orange'>Principal</div>", unsafe_allow_html=True)
        user = st.text_input(
            "Principal", value=user, placeholder="seu-email@gmail.com",
            label_visibility="collapsed", key="ui_mail_user",
        )

    with c2:
        st.markdown("<div class='orange'>Senha (app password)</div>", unsafe_allow_html=True)
        passwd = st.text_input(
            "Senha", value=passwd, type="password",
            placeholder="16 dígitos do app password (Google)",
            label_visibility="collapsed", key="ui_mail_pass",
        )

    with c3:
        st.markdown("<div class='orange'>Envio (opcional)</div>", unsafe_allow_html=True)
        to_addr = st.text_input(
            "Envio", value=to_addr, placeholder="para@dominio.com",
            label_visibility="collapsed", key="ui_mail_to",
        )

    with c4:
        st.write("")  # alinhamento
        st.write("")
        acao = st.button("TESTAR/SALVAR", use_container_width=True, key="btn_testar_salvar")

    if acao:
        # Salva na sessão
        st.session_state["MAIL_USER"] = user.strip()
        st.session_state["MAIL_APP_PASSWORD"] = passwd.strip()
        st.session_state["MAIL_TO"] = to_addr.strip()

        # Envia teste para o destinatário (Envio). Se vazio, vai para o Principal.
        try:
            _send_test_email(user.strip(), passwd.strip(), (to_addr or user).strip())
            st.success(f"E-mail de teste enviado via SSL 465 para {(to_addr or user).strip()}.")
            st.info("Dados salvos nesta sessão. (Se não aparecer, verifique a pasta Spam/Lixo.)")
        except Exception as e:
            st.error(f"Falha ao enviar o e-mail de teste: {e}")

# ==================================================
# SEÇÕES DEMAIS (Moedas/Entrada/Saída/Estado)
# → Chamamos se existirem no arquivo; se não, mostramos aviso.
# ==================================================
def _call_if_exists(fn_name: str, titulo: str):
    fn = globals().get(fn_name)
    if callable(fn):
        try:
            fn()
        except Exception as e:
            st.error(f"Erro na seção {titulo}:")
            st.exception(e)
    else:
        st.info(f"Seção **{titulo}** não encontrada (função `{fn_name}()` ausente).")

# ==================================================
# LAYOUT PRINCIPAL + ABAS
# ==================================================
st.markdown("### <span class='orange'>Interface do projeto — layout aprovado</span>", unsafe_allow_html=True)

abas = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

with abas[0]:
    secao_email()

with abas[1]:
    _call_if_exists("secao_moedas", "Moedas")

with abas[2]:
    _call_if_exists("secao_entrada", "Entrada")

with abas[3]:
    _call_if_exists("secao_saida", "Saída")

with abas[4]:
    _call_if_exists("secao_estado", "Estado")
