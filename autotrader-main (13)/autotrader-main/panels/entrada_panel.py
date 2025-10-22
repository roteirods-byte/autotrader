# ENTRADA — duas colunas lado a lado (4H e 1H) e SINAL sem quebra de linha
import streamlit as st
import pandas as pd

DEFAULT_COINS = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT",
    "ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE",
    "POL","RATS","RENDER","RUNE","SEI","SHIB","SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

def _coins_ativas():
    db = st.session_state.get("moedas_db")
    if not db: return DEFAULT_COINS
    return [s for s, v in db.items() if v.get("Ativo?", True)]

def _fmt(x, nd=3):
    try: return f"{float(x):.{nd}f}"
    except: return str(x or "")

def _badge(sinal: str) -> str:
    s = (sinal or "").upper()
    if s == "SHORT":
        return '<span style="white-space:nowrap;background:#EF4444;color:#fff;padding:2px 8px;border-radius:999px;font-weight:700;">SHORT</span>'
    if s == "LONG":
        return '<span style="white-space:nowrap;background:#22C55E;color:#0B0B0B;padding:2px 8px;border-radius:999px;font-weight:700;">LONG</span>'
    # NÃO ENTRAR sem quebrar linha:
    return '<span style="white-space:nowrap;opacity:.85">NÃO ENTRAR</span>'

def _baseline_rows():
    return [{
        "simbolo": sym, "sinal": "NAO_ENTRAR",
        "preco": 0.0, "alvo": 0.0, "ganho": 0.0, "assert": 0.0,
        "data": "", "hora": ""
    } for sym in sorted(_coins_ativas())]

def _overlay_with_signals(rows, key_signals: str):
    sigs = { (s.get("simbolo") or "").upper(): s for s in st.session_state.get(key_signals, []) }
    out = []
    for r in rows:
        s = sigs.get(r["simbolo"])
        if s:
            r = r | {
                "sinal": s.get("sinal", r["sinal"]),
                "preco": s.get("preco", r["preco"]),
                "alvo":  s.get("alvo",  r["alvo"]),
                "ganho": s.get("ganho", r["ganho"]),
                "assert":s.get("assert",r["assert"]),
                "data":  s.get("data",  r["data"]),
                "hora":  s.get("hora",  r["hora"]),
            }
        out.append(r)
    return out

def _section(titulo: str, key_signals: str):
    st.markdown(f"### {titulo}")

    base = _baseline_rows()
    rows = _overlay_with_signals(base, key_signals)

    # Cabeçalho (SINAL mais largo)
    widths = [1.2, 1.5, 1, 1, 1, 1, 1.2, 1]
    for col, h in zip(st.columns(widths), ["PARIDADE","SINAL","PREÇO","ALVO","GANHO%","ASSERT%","DATA","HORA"]):
        col.markdown(f"**{h}**")

    # Linhas
    linhas_csv = []
    for r in rows:
        c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(widths)
        c1.write(r["simbolo"])
        c2.markdown(_badge(r["sinal"]), unsafe_allow_html=True)
        c3.write(_fmt(r["preco"],3))
        c4.write(_fmt(r["alvo"],3))
        try:
            g = float(r["ganho"] or 0)
            gtxt = f"{g:.2f}"
            if g > 0:
                c5.markdown(f"<span style='color:#22C55E;font-weight:600'>{gtxt}</span>", unsafe_allow_html=True)
            elif g < 0:
                c5.markdown(f"<span style='color:#EF4444;font-weight:600'>{gtxt}</span>", unsafe_allow_html=True)
            else:
                c5.write(gtxt)
        except:
            c5.write(_fmt(r["ganho"],2))
        c6.write(_fmt(r["assert"],2))
        c7.write(str(r["data"] or ""))
        c8.write(str(r["hora"] or ""))

        linhas_csv.append({
            "PARIDADE": r["simbolo"], "SINAL": r["sinal"], "PRECO": r["preco"],
            "ALVO": r["alvo"], "GANHO%": r["ganho"], "ASSERT%": r["assert"],
            "DATA": r["data"], "HORA": r["hora"]
        })

    st.download_button(
        f"Baixar CSV — {titulo}",
        data=pd.DataFrame(linhas_csv).to_csv(index=False).encode("utf-8"),
        file_name=f"sinais_{key_signals}.csv",
        mime="text/csv"
    )

def render_entrada_panel():
    st.subheader("ENTRADA")
    col4h, col1h = st.columns(2, gap="large")  # LADO A LADO
    with col4h:
        _section("ENTRADA 4H — SWING", "signals_4h")
    with col1h:
        _section("ENTRADA 1H — POSICIONAL", "signals_1h")
