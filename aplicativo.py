# ==========================
# aplicativo.py — AUTOTRADER (versão única completa)
# ==========================
# Requisitos (Render/GitHub):
#   pip install streamlit pandas gspread google-auth ccxt
# Variáveis de ambiente:
#   SHEET_ID
#   GCP_CREDENTIALS_PATH  (ou)  GCP_CREDENTIALS_JSON
#   EXCHANGE=binance|bybit|okx   (padrão: binance)
#   ENVIAR_EMAIL_SINAIS=ON|OFF   (padrão: OFF)
#   Opcional: MAIL_* salvos no Sheets (aba EMAIL)

# === BLOCO 000 — IMPORTS/BASE ===
import os, json, ssl, smtplib, math, hashlib
from email.message import EmailMessage
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timezone
import pandas as pd
import streamlit as st

# === BLOCO 010 — TEMA/UI ===
st.set_page_config(page_title="Interface do projeto — layout aprovado", layout="wide")
st.markdown("""
<style>
 .stApp { background: #0f172a; }
 h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: #ffa41b !important; }
 .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid rgba(255,255,255,0.08); }
 .stButton>button { border-radius: 14px; font-weight: 600; }
 .ok { color:#16a34a; }
 .err { color:#ef4444; }
 .muted { opacity:.8; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

# === BLOCO 015 — PARÂMETROS DO PROJETO (CONFIRMADOS) ===
TIMEFRAME_SWING = "4H"  # Donchian/ATR em 4h
TIMEFRAME_POSICIONAL = "1D"  # Donchian/ATR em 1d
FREQUENCIA_MIN = 10  # auto-refresh alvo

APP_TZ = "America/Sao_Paulo"
SHEET_EMAIL    = "EMAIL"
SHEET_MOEDA    = "MOEDA"
SHEET_ENTRADA  = "ENTRADA"
SHEET_SAIDA    = "SAIDA"
SHEET_ESTADO   = "ESTADO"
SHEET_CONFIG   = "CONFIG"
SHEET_LOG      = "LOG"        # auditoria simples
SHEET_SINAIS   = "SINAIS"     # histórico/anti-duplicação

EMAIL_COLS   = ["principal","app_password","envio","ultimo_teste_iso"]
MOEDA_COLS   = ["moeda"]
ENTRADA_COLS = ["par","side","modo","entrada","alvo","preco_atual","pnl_pct","situacao","data","hora"]
SAIDA_COLS   = ["par","side","modo","entrada","alvo","preco_atual","pnl_pct","situacao","data","hora"]
ESTADO_COLS  = ["kpi","valor","ts_iso"]
CONFIG_COLS  = ["risco_pct","alavancagem","spread_max","slippage_max","pl_alvo_pct","funding_filtro","fuso","auto_engine","ultima_atualizacao_iso"]
LOG_COLS     = ["tipo","par","modo","side","mensagem","ts_iso"]
SINAIS_COLS  = ["sinal_id","par","modo","side","bar_time","price","atr","upper","lower","ts_iso"]

COINS_PROJETO: List[str] = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK",
    "LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB",
    "SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()

# === BLOCO 020 — GOOGLE SHEETS (conexão/util) — FIX HEADER NÃO EXCLUSIVO ===
@st.cache_resource(show_spinner=False)
def _get_gspread():
    """Conecta no Google Sheets via Service Account."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv("GCP_CREDENTIALS_JSON")
        creds_path = os.getenv("GCP_CREDENTIALS_PATH")
        if creds_json:
            info = json.loads(creds_json)
            creds = Credentials.from_service_account_info(info, scopes=scopes)
        elif creds_path and os.path.exists(creds_path):
            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        else:
            st.warning("Credenciais GCP não configuradas. Operando sem persistência.")
            return None, None
        client = gspread.authorize(creds)
        sheet_id = os.getenv("SHEET_ID")
        if not sheet_id:
            st.warning("SHEET_ID não definido. Operando sem persistência.")
            return None, None
        sh = client.open_by_key(sheet_id)
        return client, sh
    except Exception as e:
        st.error(f"Conexão Sheets falhou: {e}")
        return None, None

def _get_ws(title: str, header: List[str]):
    client, sh = _get_gspread()
    if not sh:
        return None
    try:
        ws = sh.worksheet(title)
    except Exception:
        # cria worksheet com cabeçalho correto
        ws = sh.add_worksheet(title=title, rows="2", cols=str(max(6, len(header))))
        ws.update("A1", [header])
    return ws

def _ensure_header(ws, header: List[str]):
    """Garante que a linha 1 tem exatamente o cabeçalho esperado (corrige duplicados/vazios)."""
    try:
        vals = ws.get_values("1:1") or [[]]
        cur = [c.strip().lower() for c in (vals[0] if vals else [])]
        need_fix = (len(cur) < len(header)) or any(cur[i] if i < len(cur) else "" != header[i] for i in range(len(header)))
        if need_fix:
            ws.update("A1", [header])
    except Exception:
        # como fallback, tenta escrever mesmo assim
        try:
            ws.update("A1", [header])
        except Exception:
            pass

def _read_ws_df(title: str, header: List[str]) -> pd.DataFrame:
    """
    Lê de forma tolerante:
    - Usa get_all_values (não exige cabeçalho exclusivo)
    - Ajusta colunas para 'header'
    """
    ws = _get_ws(title, header)
    if ws is None:
        return pd.DataFrame(columns=header)
    try:
        _ensure_header(ws, header)
        values = ws.get_all_values()  # lista de listas
    except Exception:
        return pd.DataFrame(columns=header)

    if not values:
        return pd.DataFrame(columns=header)

    # primeira linha é o cabeçalho atual (ignorar duplicidade)
    rows = values[1:] if len(values) > 1 else []
    if not rows:
        return pd.DataFrame(columns=header)

    # monta DF e força o schema esperado
    df = pd.DataFrame(rows)
    # corta/expande até o número de colunas do header
    if df.shape[1] >= len(header):
        df = df.iloc[:, :len(header)]
    else:
        for _ in range(len(header) - df.shape[1]):
            df[df.shape[1]] = ""
    df.columns = header

    # remove linhas 100% vazias
    df = df[~(df.replace("", pd.NA).isna().all(axis=1))].reset_index(drop=True)
    return df

def _write_ws_df(title: str, df: pd.DataFrame, header: List[str]):
    ws = _get_ws(title, header)
    if ws is None:
        return
    _ensure_header(ws, header)
    for c in header:
        if c not in df.columns:
            df[c] = ""
    df = df[header]
    payload = [header] + df.astype(str).values.tolist()
    ws.clear()
    ws.update("A1", payload)

def _append_ws_rows(title: str, rows: List[List[str]], header: List[str]):
    ws = _get_ws(title, header)
    if ws is None or not rows:
        return
    _ensure_header(ws, header)
    existing = ws.get_all_values()
    if not existing:
        ws.update("A1", [header])
    ws.append_rows(rows)
# === FIM BLOCO 020 FIX ===

# === BLOCO 030 — EMAIL (config + envio) ===
def load_email_cfg() -> dict:
    df = _read_ws_df(SHEET_EMAIL, EMAIL_COLS)
    if df.empty:
        return {"principal":"","app_password":"","envio":"","ultimo_teste_iso":""}
    return df.iloc[0].to_dict()

def save_email_cfg(cfg: dict):
    _write_ws_df(SHEET_EMAIL, pd.DataFrame([cfg], columns=EMAIL_COLS), EMAIL_COLS)

def send_test_email(cfg: dict) -> Tuple[bool, str]:
    try:
        user = cfg.get("principal","").strip()
        pwd  = cfg.get("app_password","").strip()
        to   = (cfg.get("envio") or user).strip()
        if not (user and pwd and to):
            return False, "Preencha principal, app password e destino."
        msg = EmailMessage()
        msg["Subject"] = "Teste — Autotrader"
        msg["From"] = user
        msg["To"] = to
        msg.set_content(f"Teste OK ({_now_iso()})")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
            s.login(user, pwd)
            s.send_message(msg)
        return True, f"Enviado para {to}"
    except Exception as e:
        return False, f"Erro no envio: {e}"

def send_signal_email(cfg: dict, sinais: List[Dict]):
    if not sinais:
        return
    try:
        user = cfg.get("principal","").strip()
        pwd  = cfg.get("app_password","").strip()
        to   = (cfg.get("envio") or user).strip()
        if not (user and pwd and to):
            return
        lines = []
        for s in sinais:
            lines.append(f"{s['par']}  {s['side']}  {s['modo']}  entrada={s['entrada']:.3f} alvo={s['alvo']:.3f} (ATR={s['atr']:.3f})  {s['data']} {s['hora']}")
        body = "Novos sinais:\n" + "\n".join(lines)
        msg = EmailMessage()
        msg["Subject"] = "Sinais — Autotrader"
        msg["From"] = user
        msg["To"] = to
        msg.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
            s.login(user, pwd)
            s.send_message(msg)
    except Exception:
        pass

# === BLOCO 040 — COINS (load/save) ===
def load_coins() -> List[str]:
    df = _read_ws_df(SHEET_MOEDA, MOEDA_COLS)
    if df.empty:
        return COINS_PROJETO.copy()
    coins = [str(x).strip().upper() for x in df["moeda"] if str(x).strip()]
    return sorted(set(coins))

def save_coins(coins: List[str]):
    _write_ws_df(SHEET_MOEDA, pd.DataFrame({"moeda": sorted(set(coins))}), MOEDA_COLS)

# === BLOCO 050 — CONFIG (globais) ===
def load_config() -> dict:
    df = _read_ws_df(SHEET_CONFIG, CONFIG_COLS)
    if df.empty:
        return {
            "risco_pct":"1.0","alavancagem":"5","spread_max":"0.05","slippage_max":"0.05",
            "pl_alvo_pct":"6.00","funding_filtro":"OFF","fuso":APP_TZ,"auto_engine":"ON",
            "ultima_atualizacao_iso":""
        }
    return df.iloc[0].to_dict()

def save_config(cfg: dict):
    _write_ws_df(SHEET_CONFIG, pd.DataFrame([cfg], columns=CONFIG_COLS), CONFIG_COLS)

# === BLOCO 060 — EXCHANGE (ccxt) ===
@st.cache_resource(show_spinner=False)
def _get_exchange():
    """Carrega a exchange e os mercados (swap perp USDT, quando disponível)."""
    try:
        import ccxt
        ex_id = (os.getenv("EXCHANGE") or "binance").lower()
        ex_class = getattr(ccxt, ex_id)
        ex = ex_class({"enableRateLimit": True})
        # preferir swap/perp
        try:
            ex.options = ex.options or {}
            ex.options["defaultType"] = "swap"
        except Exception:
            pass
        markets = ex.load_markets()
        return ex_id, ex, markets
    except Exception as e:
        st.warning(f"ccxt indisponível ({e}). Motores desativados.")
        return None, None, {}

def _symbol_candidates(base: str) -> List[str]:
    return [
        f"{base}/USDT:USDT",  # perp USDT (bybit/okx/binance futures)
        f"{base}/USDT",       # spot/future
    ]

def _find_symbol(base: str, markets: Dict) -> Optional[str]:
    base = base.upper()
    for s in _symbol_candidates(base):
        m = markets.get(s)
        if m and (m.get("swap") or "USDT" in s):
            return s
    return None

def _fmt_pct(x):
    try: return f"{float(x):.2f}%"
    except: return str(x)
def _fmt_px(x):
    try: return f"{float(x):.3f}"
    except: return str(x)

# === BLOCO 070 — INDICADORES (ATR / Donchian) ===
def _calc_indicadores(df: pd.DataFrame, atr_n: int = 14, don_n: int = 20) -> pd.DataFrame:
    # df: columns [ts, open, high, low, close, volume]
    out = df.copy()
    out["prev_close"] = out["close"].shift(1)
    tr1 = out["high"] - out["low"]
    tr2 = (out["high"] - out["prev_close"]).abs()
    tr3 = (out["low"] - out["prev_close"]).abs()
    out["tr"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    out["atr"] = out["tr"].rolling(atr_n).mean()
    out["don_high"] = out["high"].rolling(don_n).max()
    out["don_low"]  = out["low"].rolling(don_n).min()
    return out

# === BLOCO 080 — OHLCV (coleta segura) ===
def _fetch_ohlcv(ex, symbol: str, tf: str, limit: int = 300) -> Optional[pd.DataFrame]:
    tf_map = { "4H":"4h", "1D":"1d" }
    timeframe = tf_map.get(tf, "4h")
    try:
        raw = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not raw: return None
        df = pd.DataFrame(raw, columns=["ts","open","high","low","close","volume"])
        return df
    except Exception:
        return None

# === BLOCO 090 — SINAIS (motor: Donchian breakout + ATR) ===
def _bar_id(ts_ms: int, tf: str) -> str:
    # id textual por timeframe
    dt = datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc).astimezone()
    return f"{tf}-{dt.isoformat(timespec='minutes')}"

def _sinal_id(par, modo, side, bar_time) -> str:
    s = f"{par}|{modo}|{side}|{bar_time}"
    return hashlib.sha1(s.encode()).hexdigest()[:16]

def _ja_sinalizado(sinal_id: str) -> bool:
    df = _read_ws_df(SHEET_SINAIS, SINAIS_COLS)
    if df.empty: return False
    return sinal_id in set(df["sinal_id"].astype(str))

def _registrar_sinais_log(sinais_rows: List[List[str]]):
    if not sinais_rows: return
    _append_ws_rows(SHEET_SINAIS, sinais_rows, SINAIS_COLS)

def _append_log(tipo: str, par: str, modo: str, side: str, msg: str):
    _append_ws_rows(SHEET_LOG, [[tipo,par,modo,side,msg,_now_iso()]], LOG_COLS)

def _gerar_sinais(coins: List[str]) -> List[Dict]:
    ex_id, ex, markets = _get_exchange()
    if not ex or not markets:
        return []
    novos: List[Dict] = []

    for modo, tf in [("SWING", TIMEFRAME_SWING), ("POSICIONAL", TIMEFRAME_POSICIONAL)]:
        for base in coins:
            symbol = _find_symbol(base, markets)
            if not symbol:
                _append_log("WARN", base, modo, "", "Símbolo não encontrado")
                continue
            df = _fetch_ohlcv(ex, symbol, tf, limit=200)
            if df is None or df.shape[0] < 40:
                _append_log("WARN", base, modo, "", "OHLCV insuficiente")
                continue
            ind = _calc_indicadores(df)
            last = ind.iloc[-1]
            prev = ind.iloc[-2]
            price = float(last["close"])
            atr = float(last["atr"]) if not math.isnan(last["atr"]) else None
            upper_prev = float(prev["don_high"]) if not math.isnan(prev["don_high"]) else None
            lower_prev = float(prev["don_low"])  if not math.isnan(prev["don_low"])  else None
            if atr is None or upper_prev is None or lower_prev is None:
                continue

            bar_time = _bar_id(int(last["ts"]), tf)
            # regras simples de breakout (clássico): close rompe canal do período anterior
            long_sig  = price > upper_prev
            short_sig = price < lower_prev

            if long_sig or short_sig:
                side = "LONG" if long_sig else "SHORT"
                sinal_id = _sinal_id(base, modo, side, bar_time)
                if _ja_sinalizado(sinal_id):
                    # já registrado nesta barra → ignora
                    continue
                # alvo simples: 1x ATR a favor
                alvo = price + (atr if long_sig else -atr)
                data_local = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
                hora_local = datetime.now(timezone.utc).astimezone().strftime("%H:%M")

                item = {
                    "par": base,
                    "side": side,
                    "modo": modo,
                    "entrada": price,
                    "alvo": alvo,
                    "preco_atual": price,
                    "pnl_pct": 0.0,
                    "situacao": "NOVO",
                    "data": data_local,
                    "hora": hora_local,
                    "atr": atr,
                    "upper": upper_prev,
                    "lower": lower_prev,
                    "bar_time": bar_time,
                    "sinal_id": sinal_id
                }
                novos.append(item)
    return novos

def _salvar_sinais(novos: List[Dict]):
    if not novos: return
    # ENTRADA
    entrada_rows = []
    saida_rows   = []
    sinais_rows  = []
    for s in novos:
        entrada_rows.append([
            s["par"], s["side"], s["modo"],
            f"{s['entrada']:.6f}", f"{s['alvo']:.6f}", f"{s['preco_atual']:.6f}",
            f"{s['pnl_pct']:.4f}", s["situacao"], s["data"], s["hora"]
        ])
        # cria espelho em SAÍDA (monitoramento)
        saida_rows.append([
            s["par"], s["side"], s["modo"],
            f"{s['entrada']:.6f}", f"{s['alvo']:.6f}", f"{s['preco_atual']:.6f}",
            f"{s['pnl_pct']:.4f}", "ABERTA", s["data"], s["hora"]
        ])
        sinais_rows.append([
            s["sinal_id"], s["par"], s["modo"], s["side"], s["bar_time"],
            f"{s['entrada']:.6f}", f"{s['atr']:.6f}", f"{s['upper']:.6f}", f"{s['lower']:.6f}", _now_iso()
        ])
    _append_ws_rows(SHEET_ENTRADA, entrada_rows, ENTRADA_COLS)
    _append_ws_rows(SHEET_SAIDA,   saida_rows,   SAIDA_COLS)
    _registrar_sinais_log(sinais_rows)
    _append_log("INFO","*","*","*",(f"{len(novos)} novos sinais"),)

# === BLOCO 100 — ATUALIZAÇÃO DE PREÇOS/PNL (vivo) ===
def _calc_pnl_pct(side: str, entrada: float, px: float) -> float:
    if entrada <= 0: return 0.0
    r = (px/entrada - 1.0) * 100.0
    return r if side == "LONG" else -r

def _update_live_prices():
    ex_id, ex, markets = _get_exchange()
    if not ex or not markets: 
        return 0
    df_entrada = _read_ws_df(SHEET_ENTRADA, ENTRADA_COLS)
    df_saida   = _read_ws_df(SHEET_SAIDA, SAIDA_COLS)
    if df_saida.empty and df_entrada.empty: 
        return 0

    # conjunto de pares a consultar
    pares = set()
    for df in [df_entrada, df_saida]:
        if not df.empty:
            pares.update(df["par"].astype(str).str.upper().tolist())
    pares = sorted(pares)

    # puxa último preço de cada par
    px_map: Dict[str,float] = {}
    for base in pares:
        sym = _find_symbol(base, markets)
        if not sym: 
            continue
        try:
            ticker = ex.fetch_ticker(sym)
            last = ticker.get("last") or ticker.get("close")
            if last: px_map[base] = float(last)
        except Exception:
            continue

    # atualiza ENTRADA
    changed = False
    if not df_entrada.empty:
        for i,row in df_entrada.iterrows():
            base = str(row["par"]).upper()
            px = px_map.get(base)
            if px is None: continue
            df_entrada.at[i,"preco_atual"] = f"{px:.6f}"
            try:
                entrada = float(row["entrada"])
                side = str(row["side"]).upper()
                pnl = _calc_pnl_pct(side, entrada, px)
                df_entrada.at[i,"pnl_pct"] = f"{pnl:.4f}"
            except Exception:
                pass
            changed = True
        if changed: _write_ws_df(SHEET_ENTRADA, df_entrada, ENTRADA_COLS)

    # atualiza SAÍDA
    changed = False
    if not df_saida.empty:
        for i,row in df_saida.iterrows():
            base = str(row["par"]).upper()
            px = px_map.get(base)
            if px is None: continue
            df_saida.at[i,"preco_atual"] = f"{px:.6f}"
            try:
                entrada = float(row["entrada"])
                side = str(row["side"]).upper()
                pnl = _calc_pnl_pct(side, entrada, px)
                df_saida.at[i,"pnl_pct"] = f"{pnl:.4f}"
            except Exception:
                pass
            changed = True
        if changed: _write_ws_df(SHEET_SAIDA, df_saida, SAIDA_COLS)
    return len(px_map)

# === BLOCO 110 — SEÇÃO: E-MAIL ===
def secao_email():
    st.subheader("Configurações de e-mail")
    cfg = st.session_state.get("email_cfg") or load_email_cfg()

    c1, c2, c3, c4 = st.columns([3,2,3,1])
    with c1:
        principal = st.text_input("Principal", value=cfg.get("principal",""), key="email_principal")
    with c2:
        app_password = st.text_input("Senha (app password)", value=cfg.get("app_password",""), type="password", key="email_pass")
    with c3:
        envio = st.text_input("Envio (opcional)", value=cfg.get("envio",""), key="email_envio")
    with c4:
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
                new_cfg["ultimo_teste_iso"] = _now_iso()
                save_email_cfg(new_cfg)
                st.session_state["email_cfg"] = new_cfg
                st.success(msg)
            else:
                st.error(msg)
    cfg_show = st.session_state.get("email_cfg") or cfg
    st.caption(f"Último teste: {cfg_show.get('ultimo_teste_iso','—')}")

# === BLOCO 120 — SEÇÃO: MOEDAS ===
def secao_moedas():
    st.subheader("PAINEL DE MOEDAS")
    if "moedas" not in st.session_state:
        st.session_state["moedas"] = load_coins()
    st.session_state.setdefault("nova_moeda", "")
    st.session_state.setdefault("remover_moedas", [])

    c1, c2 = st.columns([6,1])
    with c1:
        st.text_input("Nova:", key="nova_moeda", placeholder="BTC, ETH, ...")

    def _on_add():
        val = (st.session_state.get("nova_moeda") or "").strip().upper()
        if val:
            # sem validação rígida — aceitar símbolo para teste
            if val not in st.session_state["moedas"]:
                st.session_state["moedas"].append(val)
                st.session_state["moedas"] = sorted(set(st.session_state["moedas"]))
                try:
                    save_coins(st.session_state["moedas"])
                    st.success(f"{val} adicionada e salva.", icon="✅")
                except Exception as e:
                    st.error(f"Falha ao salvar no Sheets: {e}")
        st.session_state.pop("nova_moeda", None)
        st.rerun()

    with c2:
        st.button("Adicionar", type="primary", on_click=_on_add, key="btn_add_moeda")

    st.caption("Lista atual (ordem alfabética):")
    st.dataframe(pd.DataFrame({"Moeda": st.session_state["moedas"]}), use_container_width=True, hide_index=True)

    sel = st.multiselect("Remover", options=st.session_state["moedas"], key="remover_moedas")
    def _on_del():
        if st.session_state["remover_moedas"]:
            st.session_state["moedas"] = [m for m in st.session_state["moedas"] if m not in st.session_state["remover_moedas"]]
            st.session_state["moedas"].sort()
            try:
                save_coins(st.session_state["moedas"])
                st.success("Remoção salva.", icon="✅")
            except Exception as e:
                st.error(f"Falha ao salvar no Sheets: {e}")
        st.session_state["remover_moedas"] = []
        st.rerun()
    st.button("Excluir selecionadas", disabled=not sel, on_click=_on_del, key="btn_del_moeda")

# === BLOCO 130 — SEÇÃO: ENTRADA (gera sinais + atualiza PNL) ===
def secao_entrada():
    st.subheader("Monitoramento de ENTRADA")
    cfg = load_config()
    st.caption(f"Swing = {TIMEFRAME_SWING} · Posicional = {TIMEFRAME_POSICIONAL} · Auto = {cfg.get('auto_engine','ON')} · Atualização alvo = {FREQUENCIA_MIN} min")

    # Ações
    cA, cB, cC = st.columns([1,1,2])
    with cA:
        if st.button("Gerar sinais agora", key="btn_sinais_agora"):
            coins = load_coins()
            novos = _gerar_sinais(coins)
            if novos:
                _salvar_sinais(novos)
                if (os.getenv("ENVIAR_EMAIL_SINAIS","OFF").upper() == "ON"):
                    send_signal_email(load_email_cfg(), novos)
                st.success(f"{len(novos)} sinal(is) gerado(s).", icon="✅")
            else:
                st.info("Nenhum novo sinal no momento.")
    with cB:
        if st.button("Atualizar preços/PNL", key="btn_update_pnl"):
            n = _update_live_prices()
            st.success(f"Atualizado(s) {n} par(es).", icon="✅")

    # Tabela
    df = _read_ws_df(SHEET_ENTRADA, ENTRADA_COLS)
    if not df.empty:
        # formatos
        for c in ["entrada","alvo","preco_atual"]:
            if c in df.columns:
                df[c] = df[c].apply(_fmt_px)
        if "pnl_pct" in df.columns:
            df["pnl_pct"] = df["pnl_pct"].apply(_fmt_pct)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Obs.: Breakout Donchian + ATR; alvo inicial = 1×ATR.")

# === BLOCO 140 — SEÇÃO: SAÍDA (PNL ao vivo) ===
def secao_saida():
    st.subheader("Monitoramento de SAÍDA")
    cB = st.columns([1])[0]
    with cB:
        if st.button("Atualizar PNL (Saída)", key="btn_update_pnl_saida"):
            n = _update_live_prices()
            st.success(f"Atualizado(s) {n} par(es).", icon="✅")

    df = _read_ws_df(SHEET_SAIDA, SAIDA_COLS)
    if not df.empty:
        for c in ["entrada","alvo","preco_atual"]:
            if c in df.columns:
                df[c] = df[c].apply(_fmt_px)
        if "pnl_pct" in df.columns:
            df["pnl_pct"] = df["pnl_pct"].apply(_fmt_pct)
    st.dataframe(df, use_container_width=True, hide_index=True)

# === BLOCO 151 — HELPERS (Estado) ===
def _ok(flag: bool) -> str:
    return "✅ OK" if flag else "❌ OFF"

def _count_rows(title: str, cols: list) -> int:
    try:
        df = _read_ws_df(title, cols)
        return 0 if df.empty else len(df)
    except Exception:
        return 0

# === BLOCO 150 — SEÇÃO: ESTADO/KPIs + PARÂMETROS GLOBAIS (ATUALIZADO) ===
def secao_estado():
    st.subheader("Estado / KPIs")

    # --------- Saúde do sistema ---------
    cfg  = st.session_state.get("cfg") or load_config()
    mail = load_email_cfg()
    sheets_ok = _get_gspread()[1] is not None
    email_ok  = bool((mail.get("principal") or "").strip() and (mail.get("app_password") or "").strip())
    try:
        import ccxt  # noqa
        ccxt_ok = True
    except Exception:
        ccxt_ok = False

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Google Sheets", _ok(sheets_ok))
    with c2: st.metric("E-mail", _ok(email_ok))
    with c3: st.metric("ccxt (motores)", _ok(ccxt_ok))
    with c4: st.metric("Motor automático", cfg.get("auto_engine","ON"))

    st.caption(f"Última atualização (CONFIG): {cfg.get('ultima_atualizacao_iso','—')}")

    # --------- KPIs rápidos ---------
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("Sinais (histórico)", _count_rows(SHEET_SINAIS, SINAIS_COLS))
    with k2: st.metric("Entradas (linhas)", _count_rows(SHEET_ENTRADA, ENTRADA_COLS))
    with k3: st.metric("Saídas (linhas)", _count_rows(SHEET_SAIDA, SAIDA_COLS))

    st.markdown("---")
    st.subheader("Parâmetros Globais")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        risco   = st.text_input("Risco %",       cfg.get("risco_pct","1.0"))
        spread  = st.text_input("Spread máx. %", cfg.get("spread_max","0.05"))
    with c2:
        alav    = st.text_input("Alavancagem (x)", cfg.get("alavancagem","5"))
        slip    = st.text_input("Slippage máx. %", cfg.get("slippage_max","0.05"))
    with c3:
        plalvo  = st.text_input("PL alvo %", cfg.get("pl_alvo_pct","6.00"))
        funding = st.selectbox("Filtro Funding", ["ON","OFF"], index=0 if cfg.get("funding_filtro","OFF")=="ON" else 1)
    with c4:
        fuso        = st.text_input("Fuso horário", cfg.get("fuso", APP_TZ))
        auto_engine = st.selectbox("Motor automático", ["ON","OFF"], index=0 if cfg.get("auto_engine","ON")=="ON" else 1)
        st.write("")
        if st.button("Aplicar/Salvar", key="btn_cfg_salvar"):
            new_cfg = {
                "risco_pct": risco.strip() or "1.0",
                "alavancagem": alav.strip() or "5",
                "spread_max": spread.strip() or "0.05",
                "slippage_max": slip.strip() or "0.05",
                "pl_alvo_pct": plalvo.strip() or "6.00",
                "funding_filtro": funding,
                "fuso": fuso.strip() or APP_TZ,
                "auto_engine": auto_engine,
                "ultima_atualizacao_iso": _now_iso()
            }
            save_config(new_cfg)
            st.session_state["cfg"] = new_cfg
            st.success("Parâmetros salvos.", icon="✅")


# === BLOCO 160 — SCHEDULER (auto-refresh 10 min + motor opcional) ===
def _tick_auto():
    # 1) atualiza preços
    _update_live_prices()
    # 2) se auto_engine ON: gera sinais
    cfg = load_config()
    if (cfg.get("auto_engine","ON") == "ON"):
        novos = _gerar_sinais(load_coins())
        if novos:
            _salvar_sinais(novos)
            if (os.getenv("ENVIAR_EMAIL_SINAIS","OFF").upper() == "ON"):
                send_signal_email(load_email_cfg(), novos)

def _auto_refresh():
    try:
        st.autorefresh(interval=FREQUENCIA_MIN*60*1000, key="auto_refresh_tick")
    except Exception:
        pass  # versões antigas podem não ter

# === BLOCO 170 — APP/TABS ===
st.title("Interface do projeto — layout aprovado")

# Auto
_auto_refresh()
# roda um tick leve quando carrega
try:
    if "first_load_done" not in st.session_state:
        _tick_auto()
        st.session_state["first_load_done"] = True
except Exception:
    pass

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
