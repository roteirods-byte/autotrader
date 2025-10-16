# aplicativo.py
from __future__ import annotations
import os, re, smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
from zoneinfo import ZoneInfo
from datetime import datetime
from db import get_engine, ensure_tables, fetch_table, list_required_coins

# ------------------ Config base ------------------
TZ = os.getenv("TZ", "America/Sao_Paulo")

st.set_page_config(
    page_title="Painéis | EMAIL • MOEDAS • ENTRADA • SAÍDA",
    layout="wide",
)

# ------------------ Estilos ------------------
CSS = """
<style>
:root { --orange:#ff8c00; }

/* subtítulos em laranja */
h3.title-orange { color: var(--orange); margin-bottom: .25rem; }

/* largura global dos inputs e espaçamento lateral */
div[data-baseweb="input"] input { width: 250px !important; }
.inline { display:inline-block; margin-right:20px; vertical-align:top; }

/* tabela em 1306px e sem toolbar/index */
.email-wrap { max-width:1306px; width:1306px; margin-left:0; }
div[data-testid="stElementToolbar"]{ display:none !important; }
div[data-testid="stDataFrame"] table thead th:first-child,
div[data-testid="stDataFrame"] table tbody td:first-child{ display:none; }

/* legenda */
.footer-note { opacity:.6; font-size:.85rem; }

/* tipografia da grade */
div[data-testid="stDataFrame"] div[role="grid"] { font-size: .95rem; }

/* badges (usadas em outras abas) */
.badge-long{ color:#00E676; font-weight:700; }
.badge-short{ color:#FF5252; font-weight:700; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------ Helpers ------------------
def fmt_prices(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
    return df

def fmt_perc(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
    return df

def now_brt_str() -> str:
    return datetime.now(ZoneInfo(TZ)).strftime("%d/%m/%Y %H:%M:%S")

def is_email(x:str)->bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", x))

def send_email_gmail(user:str, app_password:str, to:str, subject:str, body:str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, app_password)
        smtp.send_message(msg)

# ------------------ Dados (somente BANCO) ------------------
engine = get_engine()
ensure_tables(engine)

emails = fetch_table("emails", engine)
if emails.empty:
    emails = pd.DataFrame([{"data":"", "hora":"", "assunto":"", "mensagem":"", "status":""}])

moedas = fetch_table("moedas", engine)
if moedas.empty:
    moedas = pd.DataFrame({"simbolo": sorted(list_required_coins()), "ativo": True, "observacao": ""})
else:
    moedas = moedas.sort_values(by="simbolo", ascending=True)

entradas = fetch_table("entradas", engine)
if entradas.empty:
    entradas = pd.DataFrame([{
        "data":"", "hora":"", "moeda":"", "side":"", "preco_entrada":"",
        "stop":"", "tp":"", "score":"", "modo":""
    }])
entradas = fmt_prices(entradas, ["preco_entrada","stop","tp"])
entradas = fmt_perc(entradas, ["score"])

saidas = fetch_table("saidas", engine)
if saidas.empty:
    saidas = pd.DataFrame([{
        "data":"", "hora":"", "moeda":"", "side":"", "modo":"",
        "entrada":"", "preco_atual":"", "alvo":"", "pnl_pct":"", "situacao":""
    }])
saidas = fmt_prices(saidas, ["entrada","preco_atual","alvo"])
saidas = fmt_perc(saidas, ["pnl_pct"])

# ------------------ Layout ------------------
st.title("📊 Painéis do Operador — EMAIL • MOEDAS • ENTRADA • SAÍDA")
st.caption(f"Atualizado: {now_brt_str()} (BRT). *Somente leitura.*")

tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["✉️ EMAIL", "🪙 MOEDAS", "✅ ENTRADA", "📤 SAÍDA"])

# ================== ABA: E-MAIL ==================
with tab_email:
    st.markdown('<h3 class="title-orange">Configurações de e-mail</h3>', unsafe_allow_html=True)

    # Prefill a partir do ambiente (padrão); pode ser alterado pelo operador
    if "mail_user" not in st.session_state:
        st.session_state.mail_user = os.getenv("MAIL_USER","")
        st.session_state.mail_pwd  = os.getenv("MAIL_APP_PASSWORD","")
        st.session_state.mail_to   = os.getenv("MAIL_TO","")

    # Inputs em linha (250 px cada + 20 px de gap)
    st.markdown('<div class="inline">', unsafe_allow_html=True)
    principal = st.text_input("principal (remetente)", value=st.session_state.mail_user, key="mail_user_ui")
    st.markdown('</div><div class="inline">', unsafe_allow_html=True)
    senha = st.text_input("senha (app)", value=st.session_state.mail_pwd, type="password", key="mail_pwd_ui")
    st.markdown('</div><div class="inline">', unsafe_allow_html=True)
    envio = st.text_input("envio (destinatário)", value=st.session_state.mail_to, key="mail_to_ui")
    st.markdown('</div>', unsafe_allow_html=True)

    testar = st.button("TESTAR / SALVAR")

    if testar:
        # salva na sessão
        st.session_state.mail_user = principal.strip()
        st.session_state.mail_pwd  = senha.strip()
        st.session_state.mail_to   = envio.strip()

        # validação simples
        if not (is_email(st.session_state.mail_user) and is_email(st.session_state.mail_to)):
            st.error("Verifique os e-mails de remetente e destinatário.")
        elif not st.session_state.mail_pwd:
            st.error("Informe a senha de app do Gmail.")
        else:
            try:
                send_email_gmail(
                    st.session_state.mail_user,
                    st.session_state.mail_pwd,
                    st.session_state.mail_to,
                    "Teste Autotrader (Render)",
                    "E-mail de teste: painel online e credenciais válidas.",
                )
                st.success("Configurações salvas e e-mail de TESTE enviado com sucesso.")
            except Exception as e:
                st.error(f"Falha ao enviar: {e}")

    st.divider()
    st.markdown('<h3 class="title-orange">E-MAIL</h3>', unsafe_allow_html=True)

    # Grade 1306x160, sem toolbar e sem índice
    st.markdown('<div class="email-wrap">', unsafe_allow_html=True)
    view = emails[["data","hora","assunto","mensagem","status"]].fillna("")
    st.dataframe(view, use_container_width=False, width=1306, height=160, hide_index=True)
    st.markdown('<div class="footer-note">E-MAIL — 1306×160 px | % 2 casas • preços 3 casas • Data/Hora separadas.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============ Demais abas mantidas (sem mudanças visuais agora) ============
with tab_moedas:
    st.markdown('<h3 class="title-orange">MOEDAS (A–Z)</h3>', unsafe_allow_html=True)
    st.dataframe(moedas[["simbolo","ativo","observacao"]].fillna(""), use_container_width=True, height=420)

with tab_entrada:
    st.markdown('<h3 class="title-orange">ENTRADA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","preco_entrada","stop","tp","score","modo"]
    st.dataframe(entradas.reindex(columns=cols).fillna(""), use_container_width=True, height=420)

with tab_saida:
    st.markdown('<h3 class="title-orange">SAÍDA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","modo","entrada","preco_atual","alvo","pnl_pct","situacao"]
    st.dataframe(saidas.reindex(columns=cols).fillna(""), use_container_width=True, height=420)
