# aplicativo.py
from __future__ import annotations
import os
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
/* tipografia geral das tabelas */
div[data-testid="stDataFrame"] div[role="grid"] { font-size: 0.95rem; }

/* badges */
.badge-long  { color: #00E676; font-weight: 700; }
.badge-short { color: #FF5252; font-weight: 700; }

/* legenda */
.footer-note { opacity: 0.6; font-size: 0.85rem; }

/* esconde índice do dataframe (segurança extra além de hide_index=True) */
div[data-testid="stDataFrame"] table thead th:first-child { display:none; }
div[data-testid="stDataFrame"] table tbody td:first-child { display:none; }

/* centraliza o bloco da tabela de e-mail em 1306px */
.email-wrap { max-width: 1306px; width: 1306px; margin-left: 0; }
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

# ------------------ Dados (somente BANCO) ------------------
engine = get_engine()
ensure_tables(engine)

# EMAIL
emails = fetch_table("emails", engine)
if emails.empty:
    emails = pd.DataFrame([{"data":"", "hora":"", "assunto":"", "mensagem":"", "status":""}])

# MOEDAS
moedas = fetch_table("moedas", engine)
if moedas.empty:
    moedas = pd.DataFrame({"simbolo": sorted(list_required_coins()), "ativo": True, "observacao": ""})
else:
    moedas = moedas.sort_values(by="simbolo", ascending=True)

# ENTRADA
entradas = fetch_table("entradas", engine)
if entradas.empty:
    entradas = pd.DataFrame([{
        "data":"", "hora":"", "moeda":"", "side":"", "preco_entrada":"",
        "stop":"", "tp":"", "score":"", "modo":""
    }])
entradas = fmt_prices(entradas, ["preco_entrada","stop","tp"])
entradas = fmt_perc(entradas, ["score"])

# SAÍDA
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

# ================== ABA: EMAIL ==================
with tab_email:
    st.subheader("Configurações de e-mail")

    # Prefills vindos de ambiente (somente exibição; persistência real virá depois)
    default_user = os.getenv("MAIL_USER", "")
    default_pwd  = os.getenv("MAIL_APP_PASSWORD", "")
    default_to   = os.getenv("MAIL_TO", "")

    c1, c2, c3, c4 = st.columns([3, 3, 3, 1])
    with c1:
        principal = st.text_input("principal", value=default_user, placeholder="seu_email@provedor.com")
    with c2:
        senha = st.text_input("senha", value=default_pwd, type="password", placeholder="senha do app")
    with c3:
        envio = st.text_input("envio", value=default_to, placeholder="destinatario@provedor.com")
    with c4:
        salvar = st.button("TESTAR/SALVAR")

    if salvar:
        # Somente feedback visual por enquanto (layout). Persistência real será adicionada depois.
        st.success("Configurações salvas (sessão). Teste real será ativado em etapa posterior.")

    st.divider()

    st.subheader("EMAIL")
    # Área fixa 1306x160, sem índice
    st.markdown('<div class="email-wrap">', unsafe_allow_html=True)
    view = emails[["data","hora","assunto","mensagem","status"]].fillna("")
    st.dataframe(
        view,
        use_container_width=False,
        width=1306,
        height=160,
        hide_index=True,
    )
    st.markdown(
        '<div class="footer-note">E-MAIL — 1306×160 px | % 2 casas • preços 3 casas • Data/Hora separadas.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ================== ABA: MOEDAS ==================
with tab_moedas:
    st.subheader("MOEDAS (A–Z)")
    st.dataframe(
        moedas[["simbolo","ativo","observacao"]].fillna(""),
        use_container_width=True,
        height=420
    )
    st.markdown('<div class="footer-note">Sem coluna “alavancagem”. Ordem alfabética A–Z.</div>', unsafe_allow_html=True)

# ================== ABA: ENTRADA ==================
with tab_entrada:
    st.subheader("ENTRADA (somente leitura)")
    cols = ["data","hora","moeda","side","preco_entrada","stop","tp","score","modo"]
    view = entradas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">LONG <span class="badge-long">verde</span> • SHORT <span class="badge-short">vermelho</span>. '
        'Preços 3 casas • % 2 casas • Data/Hora separadas.</div>',
        unsafe_allow_html=True
    )

# ================== ABA: SAÍDA ==================
with tab_saida:
    st.subheader("SAÍDA (somente leitura)")
    cols = ["data","hora","moeda","side","modo","entrada","preco_atual","alvo","pnl_pct","situacao"]
    view = saidas.reindex(columns=cols).fillna("")
    st.dataframe(view, use_container_width=True, height=420)
    st.markdown(
        '<div class="footer-note">Campos: moeda, side, modo, entrada, preço atual, alvo, PnL%, situação, data, hora.</div>',
        unsafe_allow_html=True
    )
