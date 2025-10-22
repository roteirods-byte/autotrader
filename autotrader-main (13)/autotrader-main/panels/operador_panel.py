# panels/operador_panel.py  — Cartões + Lista (Streamlit puro)
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Moedas do projeto
COINS = ["AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT",
         "ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE",
         "POL","RATS","RENDER","RUNE","SEI","SHIB","SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"]

def _get_signals():
    """Lê sinais do sistema (outro módulo grava em st.session_state['signals'])."""
    return st.session_state.get("signals", [])  # lista de dicts

def _filter(signals, moeda, periodo, status_sel):
    now = datetime.utcnow()
    if periodo == "Hoje":
        dt_min = datetime(now.year, now.month, now.day)
    elif periodo == "24h":
        dt_min = now - timedelta(hours=24)
    elif periodo == "7d":
        dt_min = now - timedelta(days=7)
    else:
        dt_min = datetime.min

    out = []
    for s in signals:
        try:
            ts = s.get("timestamp")
            ts = ts if isinstance(ts, datetime) else datetime.fromisoformat(str(ts))
        except Exception:
            continue
        if ts < dt_min: 
            continue
        if moeda != "Todas" and s.get("simbolo") != moeda:
            continue
        if s.get("status", "Ativo") not in status_sel:
            continue
        out.append({**s, "timestamp": ts})
    # mais recentes primeiro
    out.sort(key=lambda x: x["timestamp"], reverse=True)
    return out

def _cards(signals):
    ativos = sum(1 for s in signals if s.get("status") == "Ativo")
    ult24 = sum(1 for s in signals if (datetime.utcnow() - s["timestamp"]) <= timedelta(hours=24))
    total = len(signals)
    c1, c2, c3 = st.columns(3)
    c1.metric("Sinais Ativos", ativos)
    c2.metric("Últimas 24h", ult24)
    c3.metric("Total no Período", total)

def _list(signals):
    if not signals:
        st.info("Sem sinais no período/filtragem.")
        return
    for s in signals:
        col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.1, 1.2, 3])
        col1.write(f"**{s.get('simbolo','-')}**")
        col2.write(f"{s.get('lado','-')}")
        price = s.get("preco")
        col3.write(f"{price:.4f}" if isinstance(price,(int,float)) else str(price))
        col4.write(s.get("timestamp").strftime("%d/%m %H:%M"))
        st_status = s.get("status","Ativo")
        col5.write(f"{st_status} — {s.get('observacao','') or ''}")
        st.divider()

def _download(signals_filtrados):
    if not signals_filtrados:
        return
    df = pd.DataFrame([
        {
            "timestamp": s["timestamp"].isoformat(timespec="seconds"),
            "simbolo": s.get("simbolo",""),
            "lado": s.get("lado",""),
            "preco": s.get("preco",""),
            "status": s.get("status",""),
            "observacao": s.get("observacao",""),
        } for s in signals_filtrados
    ])
    st.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="sinais.csv", mime="text/csv")

def render_operador_panel():
    st.subheader("OPERADOR")

    # Filtros
    c1, c2, c3 = st.columns([2,2,3])
    with c1:
        moeda = st.selectbox("Moeda", ["Todas"] + COINS, index=0)
    with c2:
        periodo = st.radio("Período", ["Hoje","24h","7d","Tudo"], horizontal=True, index=1)
    with c3:
        status_sel = st.multiselect("Status", ["Ativo","Encerrado"], default=["Ativo","Encerrado"])

    # Dados
    signals = _get_signals()
    filtrados = _filter(signals, moeda, periodo, status_sel)

    # Cartões
    _cards(filtrados)

    # Lista (linhas simples)
    _list(filtrados)

    # CSV
    _download(filtrados)
