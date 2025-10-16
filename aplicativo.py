# aplicativo.py
from __future__ import annotations
import os, re, smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
from zoneinfo import ZoneInfo
from datetime import datetime
from db import get_engine, ensure_tables, fetch_table, list_required_coins

# ============== Config ==============
TZ = os.getenv("TZ", "America/Sao_Paulo")
st.set_page_config(page_title="Painéis | EMAIL • MOEDAS • ENTRADA • SAÍDA", layout="wide")

# ============== CSS global (padrão visual) ==============
st.markdown("""
<style>
:root { --orange:#ff8c00; }

/* Abas em abóbora */
button[data-baseweb="tab"] p{ color:var(--orange) !important; font-weight:700; }
button[aria-selected="true"]{ border-bottom:3px solid var(--orange) !important; }

/* Títulos / rótulos laranja */
h3.title-orange{ color:var(--orange); margin:0 0 .6rem 0; }
.label-orange{ color:var(--orange); font-weight:700; margin:.25rem 0 .25rem; }

/* Linha de inputs: gap 20px e inputs com 250px */
div[data-testid="stHorizontalBlock"]{ gap:20px !important; }
div[data-testid="stTextInput"] input{ width:250px !important; }

/* Tabela: remover toolbar/índice e ajustar header/cor/alinhamento */
div[data-testid="stElementToolbar"]{ display:none !important; }
.email-wrap{ max-width:1306px; width:1306px; margin-left:0; }
div[data-testid="stDataFrame"] thead th{
  color:var(--orange) !important; text-align:center !important;
}
div[data-testid="stDataFrame"] thead th div{ justify-content:center !important; }
div[data-testid="stDataFrame"] tbody td:nth-child(1),
div[data-testid="stDataFrame"] thead th:nth-child(1){ width:90px !important; text-align:center; }
div[data-testid="stDataFrame"] tbody td:nth-child(2),
div[data-testid="stDataFrame"] thead th:nth-child(2){ width:90px !important; text-align:center; }

/* Tipografia da grid e legenda */
div[data-testid="stDataFrame"] div[role="grid"]{ font-size:.95rem; }
.footer-note{ opacity:.6; font-size:.85rem; }
.badge-long{ color:#00E676; font-weight:700; }
.badge-short{ color:#FF5252; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ============== Helpers ==============
def fmt_prices(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
    return df
def fmt_perc(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
    return df
def now_brt_str() -> str: return datetime.now(ZoneInfo(TZ)).strftime("%d/%m/%Y %H:%M:%S")
def is_email(x:str)->bool: return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", x))
def send_email_gmail(user:str, app_password:str, to:str, subject:str, body:str):
    msg = MIMEText(body, "plain", "utf-8"); msg["Subject"]=subject; msg["From"]=user; msg["To"]=to
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
        s.ehlo(); s.starttls(); s.login(user, app_password); s.send_message(msg)

# ============== Dados (somente banco) ==============
engine = get_engine(); ensure_tables(engine)

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
    entradas = pd.DataFrame([{"data":"", "hora":"", "moeda":"", "side":"",
                              "preco_entrada":"","stop":"","tp":"","score":"","modo":""}])
entradas = fmt_prices(entradas, ["preco_entrada","stop","tp"]); entradas = fmt_perc(entradas, ["score"])

saidas = fetch_table("saidas", engine)
if saidas.empty:
    saidas = pd.DataFrame([{"data":"", "hora":"", "moeda":"", "side":"", "modo":"",
                            "entrada":"","preco_atual":"","alvo":"","pnl_pct":"","situacao":""}])
saidas = fmt_prices(saidas, ["entrada","preco_atual","alvo"]); saidas = fmt_perc(saidas, ["pnl_pct"])

# ============== Layout ==============
st.title("📊 Painéis do Operador — EMAIL • MOEDAS • ENTRADA • SAÍDA")
st.caption(f"Atualizado: {now_brt_str()} (BRT). *Somente leitura.*")

tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["✉️ EMAIL", "🪙 MOEDAS", "✅ ENTRADA", "📤 SAÍDA"])

# -------- E-MAIL --------
with tab_email:
    st.markdown('<h3 class="title-orange">CORREIO ELETRÔNICO</h3>', unsafe_allow_html=True)

    # sessão (carrega ENV só 1x)
    if "mail_user" not in st.session_state:
        st.session_state.mail_user = os.getenv("MAIL_USER","")
        st.session_state.mail_pwd  = os.getenv("MAIL_APP_PASSWORD","")
        st.session_state.mail_to   = os.getenv("MAIL_TO","")

    # Linha única: rótulo + input (3x) + botão
    c1,c2,c3,c4,c5,c6,c7 = st.columns([0.8,2.6, 0.8,2.6, 0.8,2.6, 1.4], gap="small")
    with c1: st.markdown('<div class="label-orange">Principal:</div>', unsafe_allow_html=True)
    with c2: principal = st.text_input("", value=st.session_state.mail_user, key="mail_user_ui", label_visibility="collapsed")
    with c3: st.markdown('<div class="label-orange">Senha:</div>', unsafe_allow_html=True)
    with c4: senha = st.text_input("", value=st.session_state.mail_pwd, type="password", key="mail_pwd_ui", label_visibility="collapsed")
    with c5: st.markdown('<div class="label-orange">Envio:</div>', unsafe_allow_html=True)
    with c6: envio = st.text_input("", value=st.session_state.mail_to, key="mail_to_ui", label_visibility="collapsed")
    with c7: testar = st.button("TESTAR/SALVAR", use_container_width=True)

    if testar:
        st.session_state.mail_user = principal.strip()
        st.session_state.mail_pwd  = senha.strip()
        st.session_state.mail_to   = envio.strip()
        if not (is_email(st.session_state.mail_user) and is_email(st.session_state.mail_to)):
            st.error("Verifique os e-mails de remetente e destinatário.")
        elif not st.session_state.mail_pwd:
            st.error("Informe a senha de app do Gmail.")
        else:
            try:
                send_email_gmail(st.session_state.mail_user, st.session_state.mail_pwd,
                                 st.session_state.mail_to, "Teste Autotrader", "Painel OK.")
                st.success("Configurações salvas e e-mail de TESTE enviado com sucesso.")
            except Exception as e:
                st.error(f"Falha ao enviar: {e}")

    st.divider()
    st.markdown('<h3 class="title-orange">CORREIO ELETRÔNICO</h3>', unsafe_allow_html=True)

    # Tabela 1306×160
    st.markdown('<div class="email-wrap">', unsafe_allow_html=True)
    view = emails[["data","hora","assunto","mensagem","status"]].fillna("")
    st.dataframe(view, use_container_width=False, width=1306, height=160, hide_index=True)
    st.markdown('<div class="footer-note">CORREIO ELETRÔNICO — 1306×160 px | % 2 casas • preços 3 casas • Data/Hora separadas.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- MOEDAS --------
with tab_moedas:
    st.markdown('<h3 class="title-orange">MOEDAS (A–Z)</h3>', unsafe_allow_html=True)
    st.dataframe(moedas[["simbolo","ativo","observacao"]].fillna(""), use_container_width=True, height=420)

# -------- ENTRADA --------
with tab_entrada:
    st.markdown('<h3 class="title-orange">ENTRADA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","preco_entrada","stop","tp","score","modo"]
    st.dataframe(entradas.reindex(columns=cols).fillna(""), use_container_width=True, height=420)

# -------- SAÍDA --------
with tab_saida:
    st.markdown('<h3 class="title-orange">SAÍDA (somente leitura)</h3>', unsafe_allow_html=True)
    cols = ["data","hora","moeda","side","modo","entrada","preco_atual","alvo","pnl_pct","situacao"]
    st.dataframe(saidas.reindex(columns=cols).fillna(""), use_container_width=True, height=420)
