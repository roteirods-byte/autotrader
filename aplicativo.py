# aplicativo.py — cole tudo este arquivo

import os
import json
from datetime import datetime
from typing import Tuple, List, Dict

import streamlit as st
import pandas as pd
import re

# ====== Fuso / versão do app ======
from zoneinfo import ZoneInfo
APP_TZ = "America/Sao_Paulo"
APP_VERSION = (os.getenv("RENDER_GIT_COMMIT") or os.getenv("COMMIT_HASH", "") or "")[:7]

# ====== E-mail (teste) ======
import smtplib, ssl
from email.message import EmailMessage

# ====== Google Sheets ======
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.getenv("SHEET_ID", "").strip()

EMAIL_SHEET   = "EMAIL"
EMAIL_COLS    = ["principal", "app_password", "envio", "ultimo_teste_iso"]
MOEDA_SHEET   = "MOEDA"
MOEDA_COLS    = ["moeda", "ativo", "criado_em_iso"]
ENTRADA_SHEET = "ENTRADA"
ENTRADA_COLS  = ["moeda", "preco", "quantidade", "quando_iso"]
SAIDA_SHEET   = "SAIDA"
SAIDA_COLS    = ["moeda", "preco", "quantidade", "quando_iso"]
ESTADO_SHEET  = "ESTADO"
ESTADO_COLS   = ["item", "status", "quando_iso"]


# ========== THEME / CSS ==========
st.set_page_config(page_title="Interface do projeto", layout="wide")
st.markdown("""
<style>
 .stApp { background:#0f172a; }
 h1, h2, h3, .stTabs [data-baseweb="tab"] p, .stTextInput label { color:#ffa41b !important; }
 .stTabs [data-baseweb="tab-list"]{ border-bottom:1px solid rgba(255,255,255,.08); }

 /* esconder instruções automáticas */
 [data-testid="stInputInstructions"],
 .stTextInput small,
 .stForm [data-testid="stInputInstructions"],
 .stForm small,
 .stTextInput div[aria-live="polite"] { display:none !important; }

 /* caixas padrão: fundo/borda, altura e foco */
 .stTextInput>div>div{
   background:#1e293b !important; border:1px solid rgba(255,255,255,.18);
   border-radius:10px; height:40px; display:flex; align-items:center;
 }
 .stTextInput>div>div:focus-within{ outline:1px solid #334155 !important; }
 .stTextInput input{ width:100% !important; color:#fff !important; padding:8px 12px; }
 #email-row input:focus{ outline:none !important; box-shadow:none !important; }

 /* ESCOPO DO PAINEL DE E-MAIL */
 #email-row .stColumns{ gap:12px !important; }
 #email-row .fix250 .stTextInput>div>div{ width:250px !important; max-width:250px !important; }
 #email-row .fix250 [data-baseweb="input"]{ width:250px !important; max-width:250px !important; }

 /* botão laranja com mesma altura */
 .stButton>button{
   background:#ffa41b !important; color:#0f172a !important; border:0 !important;
   border-radius:14px; font-weight:700; height:40px; padding:0 16px;
 }
 .stButton>button:hover{ filter:brightness(1.05); }

 /* faixa de sucesso compacta */
 .stAlert{ padding:10px 14px !important; border-radius:10px !important; width:max-content; }
</style>
""", unsafe_allow_html=True)


# ========== UTILS ==========
def _now_local() -> datetime:
    return datetime.now(ZoneInfo(APP_TZ))

def _now_iso() -> str:
    return _now_local().isoformat()

def _is_email(s: str) -> bool:
    if not s: return False
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s) is not None


@st.cache_resource
def _gs_client():
    """Autentica no Google Sheets (JSON em env ou arquivo secreto)."""
    creds_json = (os.getenv("GCP_CREDENTIALS_JSON") or "").strip()
    if not creds_json:
        path = (os.getenv("GCP_CREDENTIALS_PATH") or "").strip()
        if path:
            full = path if path.startswith("/") else f"/etc/secrets/{path}"
            try:
                with open(full, "r", encoding="utf-8") as f:
                    creds_json = f.read()
            except Exception as e:
                raise RuntimeError(f"Não foi possível ler a chave do Google em {full}: {e}")

    if not creds_json:
        raise RuntimeError("Credencial do Google ausente. Configure GCP_CREDENTIALS_JSON ou GCP_CREDENTIALS_PATH.")

    try:
        data = json.loads(creds_json)
    except Exception:
        data = json.loads(creds_json.encode("utf-8").decode("unicode_escape"))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(data, scopes=scopes)
    return gspread.Client(auth=creds)

def _open_sheet(sheet_id: str):
    if not sheet_id:
        raise RuntimeError("SHEET_ID não configurado.")
    gc = _gs_client()
    return gc.open_by_key(sheet_id)

def _get_ws(sh, title: str, header: List[str]):
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows="1000", cols=str(max(6, len(header))))
        ws.update([header])
    head = ws.row_values(1)
    if head != header:
        ws.resize(rows=1)
        ws.update([header])
    return ws

def _read_ws_df(title: str, header: List[str]) -> pd.DataFrame:
    sh = _open_sheet(SHEET_ID)
    ws = _get_ws(sh, title, header)
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=header)
    else:
        df = df.reindex(columns=header)
    return df

def _write_ws_df(title: str, header: List[str], df: pd.DataFrame):
    sh = _open_sheet(SHEET_ID)
    ws = _get_ws(sh, title, header)
    if df.empty:
        ws.resize(rows=1)
        ws.update([header])
        return
    ws.resize(rows=len(df) + 1)
    ws.update([header] + df.astype(str).values.tolist())


# ========== EMAIL: carregar/salvar + enviar teste ==========
def load_email_cfg() -> Dict[str, str]:
    try:
        df = _read_ws_df(EMAIL_SHEET, EMAIL_COLS)
        if df.empty:
            return {"principal": "", "app_password": "", "envio": "", "ultimo_teste_iso": ""}
        row = df.iloc[0].to_dict()
        return {k: (row.get(k) or "") for k in EMAIL_COLS}
    except Exception:
        return {"principal": "", "app_password": "", "envio": "", "ultimo_teste_iso": ""}

def save_email_cfg(cfg: Dict[str, str]) -> None:
    df = pd.DataFrame([cfg], columns=EMAIL_COLS)
    _write_ws_df(EMAIL_SHEET, EMAIL_COLS, df)

def send_test_email(cfg: dict) -> Tuple[bool, str]:
    try:
        user = (cfg.get("principal") or "").strip()
        pwd  = (cfg.get("app_password") or "").strip()
        to   = (cfg.get("envio") or user).strip()
        if not (user and pwd and to):
            return False, "Preencha principal, senha e envio."

        agora = _now_local()
        body  = f"teste ok - {agora.strftime('%d/%m/%Y')} - {agora.strftime('%H:%M')}"
        msg = EmailMessage()
        msg["Subject"] = "Teste — Autotrader"
        msg["From"] = user
        msg["To"] = to
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
            s.login(user, pwd)
            s.send_message(msg)
        return True, f"Enviado para {to}"
    except Exception as e:
        return False, f"Erro no envio: {e}"


# ========== UI: Título ==========
st.title("Interface do projeto")
st.caption(f"versão do app: {APP_VERSION or 'local'}")


# ========== PAINEL: E-mail ==========
def secao_email():
    st.subheader("Configurações de e-mail")

    # carrega cfg da planilha uma única vez por sessão
    if "email_principal" not in st.session_state:
        cfg = load_email_cfg()
        st.session_state["email_principal"] = cfg.get("principal","")
        st.session_state["email_pass"]     = cfg.get("app_password","")
        # auto-preenche envio com principal, se vazio
        st.session_state["email_envio"]    = (cfg.get("envio") or cfg.get("principal") or "")

    # último teste (para exibir ao lado do título do bloco)
    cfg_tmp = {
        "ultimo_teste_iso": load_email_cfg().get("ultimo_teste_iso","")
    }
    colt1, colt2 = st.columns([6,1])
    with colt2:
        if cfg_tmp["ultimo_teste_iso"]:
            try:
                dt = datetime.fromisoformat(cfg_tmp["ultimo_teste_iso"]).astimezone(ZoneInfo(APP_TZ))
                st.caption(f"último: {dt.strftime('%H:%M')}")
            except Exception:
                pass

    # container identificado para CSS escopado (#email-row)
    st.markdown('<div id="email-row">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.7])

    with c1:
        st.markdown('<div class="fix250">', unsafe_allow_html=True)
        principal = st.text_input("principal", value=st.session_state.get("email_principal",""))
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="fix250">', unsafe_allow_html=True)
        senha = st.text_input("senha", value=st.session_state.get("email_pass",""), type="password")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="fix250">', unsafe_allow_html=True)
        envio = st.text_input("envio", value=st.session_state.get("email_envio",""))
        st.markdown('</div>', unsafe_allow_html=True)
        # dica de validação simples
        if envio and not _is_email(envio):
            st.markdown("<span style='color:#f87171;'>e-mail inválido</span>", unsafe_allow_html=True)

    with c4:
        ready = bool((principal or "").strip() and (senha or "").strip() and (not envio or _is_email(envio)))
        enviar = st.button("TESTAR/SALVAR", disabled=not ready)

    st.markdown("</div>", unsafe_allow_html=True)

    if enviar:
        cfg = {
            "principal": (principal or "").strip(),
            "app_password": (senha or "").strip(),
            "envio": ((envio or principal) or "").strip(),
            "ultimo_teste_iso": ""
        }
        ok, msg = send_test_email(cfg)
        if ok:
            agora = _now_local()
            cfg["ultimo_teste_iso"] = agora.isoformat()
            save_email_cfg(cfg)
            st.session_state["email_principal"] = cfg["principal"]
            st.session_state["email_pass"] = cfg["app_password"]
            st.session_state["email_envio"] = cfg["envio"]
            col_ok, _ = st.columns([1,3])
            with col_ok:
                st.success(f"✔ Enviado às {agora.strftime('%H:%M')}", icon="✅")
        else:
            st.error("Não foi possível enviar. Confira os dados e tente novamente.")
            st.caption(msg)


# ========== PAINEL: Moedas ==========
def _lista_moedas_padrao() -> List[str]:
    return [
        "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT","ETH","FET","FIL","FLUX",
        "ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB","SOL",
        "SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
    ]

def secao_moedas():
    st.subheader("PAINEL DE MOEDAS")
    df = _read_ws_df(MOEDA_SHEET, MOEDA_COLS)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.caption("Nova moeda (lista padrão em ordem alfabética)")
        lista = _lista_moedas_padrao()
        nova = st.selectbox("nova", lista, index=lista.index("BTC"), label_visibility="collapsed")
    with c2:
        st.write("")
        st.write("")
        if st.button("Adicionar"):
            if (df["moeda"] == nova).any():
                st.info("Moeda já cadastrada.")
            else:
                add = pd.DataFrame([{"moeda": nova, "ativo": "sim", "criado_em_iso": _now_iso()}])
                df = pd.concat([df, add], ignore_index=True)
                _write_ws_df(MOEDA_SHEET, MOEDA_COLS, df)
                st.success(f"{nova} adicionada.", icon="✅")

    st.divider()
    st.caption("Atuais:")
    if df.empty:
        st.write("Nenhuma moeda cadastrada.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ========== PAINEL: Entrada ==========
def secao_entrada():
    st.subheader("Entradas")
    df = _read_ws_df(ENTRADA_SHEET, ENTRADA_COLS)
    with st.expander("Nova entrada"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("moeda")
        with c2:
            p = st.number_input("preço", min_value=0.0, step=0.01, format="%.2f")
        with c3:
            q = st.number_input("quantidade", min_value=0.0, step=0.0001, format="%.4f")
        if st.button("Salvar entrada"):
            if m:
                add = pd.DataFrame([{"moeda": m.upper(), "preco": p, "quantidade": q, "quando_iso": _now_iso()}])
                df = pd.concat([df, add], ignore_index=True)
                _write_ws_df(ENTRADA_SHEET, ENTRADA_COLS, df)
                st.success("Entrada salva.", icon="✅")
            else:
                st.warning("Informe a moeda.")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ========== PAINEL: Saída ==========
def secao_saida():
    st.subheader("Saídas")
    df = _read_ws_df(SAIDA_SHEET, SAIDA_COLS)
    with st.expander("Nova saída"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("moeda ")
        with c2:
            p = st.number_input("preço ", min_value=0.0, step=0.01, format="%.2f")
        with c3:
            q = st.number_input("quantidade ", min_value=0.0, step=0.0001, format="%.4f")
        if st.button("Salvar saída"):
            if m:
                add = pd.DataFrame([{"moeda": m.upper(), "preco": p, "quantidade": q, "quando_iso": _now_iso()}])
                df = pd.concat([df, add], ignore_index=True)
                _write_ws_df(SAIDA_SHEET, SAIDA_COLS, df)
                st.success("Saída salva.", icon="✅")
            else:
                st.warning("Informe a moeda.")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ========== PAINEL: Estado ==========
def _status_google_sheets() -> Tuple[str, str]:
    try:
        sh = _open_sheet(SHEET_ID)
        _ = [ws.title for ws in sh.worksheets()]
        return ("OK", _now_iso())
    except Exception as e:
        return (f"ERRO: {e}", _now_iso())

def _status_ccxt() -> Tuple[str, str]:
    try:
        import ccxt  # noqa: F401
        return ("OK", _now_iso())
    except Exception:
        return ("NÃO INSTALADO", _now_iso())

def secao_estado():
    st.subheader("Estado do sistema")

    col1, col2 = st.columns(2)
    with col1:
        gs_status, quando = _status_google_sheets()
        st.write(f"**Google Sheets**: {gs_status}")
        st.caption(quando)
    with col2:
        cx, quando2 = _status_ccxt()
        st.write(f"**ccxt**: {cx}")
        st.caption(quando2)

    st.markdown("### Manutenção")
    col3, col4 = st.columns([1,1])
    with col3:
        if st.button("Forçar atualização (limpar cache)"):
            try: st.cache_data.clear()
            except: pass
            try: st.cache_resource.clear()
            except: pass
            st.success("Cache limpo. Recarregando…")
            st.experimental_rerun()
    with col4:
        st.info(f"Versão atual: {APP_VERSION or 'local'}")


# ========== TABS ==========
tabs = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])
with tabs[0]:  # E-mail
    secao_email()
with tabs[1]:  # Moedas
    secao_moedas()
with tabs[2]:  # Entrada
    secao_entrada()
with tabs[3]:  # Saída
    secao_saida()
with tabs[4]:  # Estado
    secao_estado()
