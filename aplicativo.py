# ==========================
# aplicativo.py  —  AUTOTRADER (layout aprovado)
# ==========================
# Requisitos: streamlit, pandas, gspread, google-auth
# Env: SHEET_ID, GCP_CREDENTIALS_PATH (ou GCP_CREDENTIALS_JSON), opcionalmente MAIL_* (salvos no Sheets também)

import os, json, ssl, smtplib, traceback
from email.message import EmailMessage
from typing import List, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
import streamlit as st

# ======= CONFIGURAÇÃO DE PÁGINA / ESTILO =======
st.set_page_config(page_title="Interface do projeto — layout aprovado", layout="wide")
st.markdown("""
<style>
    .stApp { background: #0f172a; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: #ffa41b !important; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid rgba(255,255,255,0.08); }
    .stButton>button { border-radius: 14px; font-weight: 600; }
    .small { font-size: 0.82rem; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# ======= CONSTANTES =======
APP_TZ = "America/Sao_Paulo"

COINS_PROJETO: List[str] = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK",
    "LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB",
    "SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

SHEET_EMAIL = "EMAIL"
SHEET_MOEDA = "MOEDA"
SHEET_ENTRADA = "ENTRADA"
SHEET_SAIDA = "SAIDA"
SHEET_ESTADO = "ESTADO"

EMAIL_COLS = ["principal", "app_password", "envio", "ultimo_teste_iso"]
MOEDA_COLS = ["moeda"]
ENTRADA_COLS = ["par","side","modo","entrada","alvo","preco_atual","pnl_pct","situacao","data","hora"]
SAIDA_COLS   = ["par","side","modo","entrada","alvo","preco_atual","pnl_pct","situacao","data","hora"]
ESTADO_COLS  = ["kpi","valor","ts_iso"]

# ======= UTIL =======
def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()

@st.cache_resource(show_spinner=False)
def _get_gspread():
    """Conecta ao Google Sheets usando credenciais do serviço."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_json = os.getenv("GCP_CREDENTIALS_JSON")
        creds_path = os.getenv("GCP_CREDENTIALS_PATH")
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        if creds_json:
            info = json.loads(creds_json)
            creds = Credentials.from_service_account_info(info, scopes=scopes)
        elif creds_path and os.path.exists(creds_path):
            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        else:
            st.warning("Credenciais GCP não configuradas. Operando em modo local (sem persistência).")
            return None, None
        client = gspread.authorize(creds)
        sheet_id = os.getenv("SHEET_ID")
        if not sheet_id:
            st.warning("SHEET_ID não definido. Operando em modo local (sem persistência).")
            return None, None
        sh = client.open_by_key(sheet_id)
        return client, sh
    except Exception as e:
        st.error(f"Falha ao conectar no Google Sheets: {e}")
        return None, None

def _get_ws(title: str, cols: List[str]):
    client, sh = _get_gspread()
    if not sh:
        return None  # sem persistência
    try:
        ws = sh.worksheet(title)
    except Exception:
        # cria worksheet com cabeçalho
        rows, cols_n = 2, max(5, len(cols))
        ws = sh.add_worksheet(title=title, rows=str(rows), cols=str(cols_n))
        ws.update("A1", [cols])
    return ws

def _read_ws_df(title: str, req_cols: List[str]) -> pd.DataFrame:
    ws = _get_ws(title, req_cols)
    if ws is None:
        return pd.DataFrame(columns=req_cols)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame(columns=req_cols)
    header = [h.strip().lower() for h in values[0]]
    rows = values[1:]
    df = pd.DataFrame(rows, columns=header[:len(rows[0])] if rows else header).rename(columns=str.lower)
    # garante colunas
    for c in req_cols:
        if c not in df.columns:
            df[c] = ""
    df = df[req_cols]
    # remove linhas vazias
    df = df[~(df.eq("").all(axis=1))]
    return df.reset_index(drop=True)

def _write_ws_df(title: str, df: pd.DataFrame, req_cols: List[str]):
    ws = _get_ws(title, req_cols)
    if ws is None:
        return
    # garante colunas
    for c in req_cols:
        if c not in df.columns:
            df[c] = ""
    df = df[req_cols]
    data = [req_cols] + df.astype(str).values.tolist()
    ws.clear()
    ws.update("A1", data)

def _fmt_pct(x) -> str:
    try:
        return f"{float(x):.2f}%"
    except:  # noqa
        return str(x)

# ======= EMAIL =======
def load_email_cfg() -> dict:
    df = _read_ws_df(SHEET_EMAIL, EMAIL_COLS)
    if df.empty:
        return {"principal":"","app_password":"","envio":"","ultimo_teste_iso":""}
    return df.iloc[0].to_dict()

def save_email_cfg(cfg: dict):
    df = pd.DataFrame([cfg], columns=EMAIL_COLS)
    _write_ws_df(SHEET_EMAIL, df, EMAIL_COLS)

def send_test_email(cfg: dict) -> Tuple[bool, str]:
    try:
        user = cfg.get("principal","").strip()
        pwd  = cfg.get("app_password","").strip()
        to   = (cfg.get("envio") or user).strip()
        if not (user and pwd and to):
            return False, "Preencha e salve: principal, app password e destino."
        msg = EmailMessage()
        msg["Subject"] = "Teste — Autotrader"
        msg["From"] = user
        msg["To"] = to
        msg.set_content(f"Teste OK ({now_iso()})")
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(user, pwd)
            server.send_message(msg)
        return True, f"Enviado para {to}"
    except Exception as e:
        return False, f"Erro no envio: {e}"

# ======= MOEDAS =======
def load_coins() -> List[str]:
    df = _read_ws_df(SHEET_MOEDA, MOEDA_COLS)
    if df.empty:
        return COINS_PROJETO.copy()
    coins = [str(x).strip().upper() for x in df["moeda"] if str(x).strip()]
    return sorted(set(coins))

def save_coins(coins: List[str]):
    df = pd.DataFrame({"moeda": sorted(set(coins))})
    _write_ws_df(SHEET_MOEDA, df, MOEDA_COLS)

# ======= ABAS =======
def secao_email():
    st.subheader("Configurações de e-mail")
    cfg = st.session_state.get("email_cfg") or load_email_cfg()
    col1, col2, col3, col4 = st.columns([3,2,3,1])
    with col1:
        principal = st.text_input("Principal", value=cfg.get("principal",""), key="email_principal")
    with col2:
        app_password = st.text_input("Senha (app password)", value=cfg.get("app_password",""), type="password", key="email_pass")
    with col3:
        envio = st.text_input("Envio (opcional)", value=cfg.get("envio",""), key="email_envio")
    with col4:
        st.markdown("&nbsp;")
        if st.button("TESTAR/SALVAR", key="btn_email_testar"):
            new_cfg = {
                "principal": st.session_state.get("email_principal","").strip(),
                "app_password": st.session_state.get("email_pass","").strip(),
                "envio": st.session_state.get("email_envio","").strip(),
                "ultimo_teste_iso": ""
            }
            ok, msg = send_test_email(new_cfg)
            if ok:
                new_cfg["ultimo_teste_iso"] = now_iso()
                save_email_cfg(new_cfg)
                st.session_state["email_cfg"] = new_cfg
                st.success(msg)
            else:
                st.error(msg)

    # rodapé
    cfg_show = st.session_state.get("email_cfg") or cfg
    st.caption(f"Último teste: {cfg_show.get('ultimo_teste_iso','—')}")

def secao_moedas():
    st.subheader("PAINEL DE MOEDAS")

    # Estado
    if "moedas" not in st.session_state:
        st.session_state["moedas"] = load_coins()
    st.session_state.setdefault("nova_moeda", "")
    st.session_state.setdefault("remover_moedas", [])

    # Add
    c1, c2 = st.columns([6,1])
    with c1:
        st.text_input("Nova:", key="nova_moeda", placeholder="BTC, ETH, ...")
    def _on_add():
        val = (st.session_state.get("nova_moeda") or "").strip().upper()
        if val:
            if val not in st.session_state["moedas"]:
                st.session_state["moedas"].append(val)
                st.session_state["moedas"] = sorted(set(st.session_state["moedas"]))
                try:
                    save_coins(st.session_state["moedas"])
                except Exception as e:
                    st.error(f"Falha ao salvar no Sheets: {e}")
        st.session_state.pop("nova_moeda", None)
        st.rerun()
    with c2:
        st.button("Adicionar", type="primary", on_click=_on_add, key="btn_add_moeda")

    st.caption("Lista atual (ordem alfabética):")
    df = pd.DataFrame({"Moeda": st.session_state["moedas"]})
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Remover
    sel = st.multiselect("Remover", options=st.session_state["moedas"], key="remover_moedas")
    def _on_del():
        if st.session_state["remover_moedas"]:
            st.session_state["moedas"] = [m for m in st.session_state["moedas"] if m not in st.session_state["remover_moedas"]]
            st.session_state["moedas"].sort()
            try:
                save_coins(st.session_state["moedas"])
            except Exception as e:
                st.error(f"Falha ao salvar no Sheets: {e}")
        st.session_state["remover_moedas"] = []
        st.rerun()
    st.button("Excluir selecionadas", disabled=not sel, on_click=_on_del, key="btn_del_moeda")

def _ensure_sheet(title: str, cols: List[str]):
    df = _read_ws_df(title, cols)
    if df.empty:
        _write_ws_df(title, pd.DataFrame(columns=cols), cols)

def secao_entrada():
    st.subheader("Monitoramento de ENTRADA")
    _ensure_sheet(SHEET_ENTRADA, ENTRADA_COLS)
    df = _read_ws_df(SHEET_ENTRADA, ENTRADA_COLS)
    # formatação leve
    if not df.empty and "pnl_pct" in df.columns:
        df["pnl_pct"] = df["pnl_pct"].apply(_fmt_pct)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Obs.: esta aba exibirá sinais e cálculos assim que implantarmos a estratégia. (esqueleto pronto)")

def secao_saida():
    st.subheader("Monitoramento de SAÍDA")
    _ensure_sheet(SHEET_SAIDA, SAIDA_COLS)
    df = _read_ws_df(SHEET_SAIDA, SAIDA_COLS)
    if not df.empty and "pnl_pct" in df.columns:
        df["pnl_pct"] = df["pnl_pct"].apply(_fmt_pct)
    st.dataframe(df, use_container_width=True, hide_index=True)

def secao_estado():
    st.subheader("Estado / KPIs")
    _ensure_sheet(SHEET_ESTADO, ESTADO_COLS)
    df = _read_ws_df(SHEET_ESTADO, ESTADO_COLS)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Logs/KPIs de auditoria serão preenchidos automaticamente pelo sistema.")

# ======= APP =======
st.title("Interface do projeto — layout aprovado")
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
