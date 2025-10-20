# SAÍDA — igual ao modelo: formulário no topo + lista de operações
import streamlit as st
from datetime import datetime

DEFAULT_COINS = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT",
    "ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE",
    "POL","RATS","RENDER","RUNE","SEI","SHIB","SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

def _coins_ativas():
    db = st.session_state.get("moedas_db")
    if not db: return DEFAULT_COINS
    return [s for s, v in db.items() if v.get("Ativo?", True)]

def _pnl(side: str, entrada: float, atual: float) -> float:
    try:
        e = float(entrada); a = float(atual)
        if e <= 0: return 0.0
        pct = (a - e)/e * 100.0
        return pct if (side or "").upper() == "LONG" else -pct
    except:
        return 0.0

def render_saida_panel():
    st.subheader("SAÍDA")

    # --- Formulário de inclusão ---
    c1,c2,c3,c4,c5,c6 = st.columns([1.2,1.2,1.5,1,0.8,1.2])
    with c1:
        par = st.selectbox("Par", _coins_ativas(), index= _coins_ativas().index("BTC") if "BTC" in _coins_ativas() else 0, key="saida_par")
    with c2:
        side = st.segmented_control("Side", options=["LONG","SHORT"], key="saida_side")  # precisa Streamlit >=1.36; se faltar, use radio
    with c3:
        modo = st.selectbox("Modo", ["Swing-friendly","Posicional"], key="saida_modo")
    with c4:
        entrada = st.number_input("Entrada", min_value=0.0, value=0.0, step=0.0001, format="%.6f", key="saida_entrada")
    with c5:
        alav = st.number_input("Alav", min_value=1, value=5, step=1, key="saida_alav")
    with c6:
        add = st.button("Adicionar Operação", use_container_width=True)

    if "ops_saida" not in st.session_state:
        st.session_state.ops_saida = []

    if add:
        agora = datetime.now()
        st.session_state.ops_saida.append({
            "par": par, "side": side, "modo": modo,
            "entrada": float(entrada or 0),
            "alvo": 0.0,
            "preco_atual": 0.0,
            "pnl": 0.0,
            "situacao": "-",
            "data": agora.strftime("%Y-%m-%d"),
            "hora": agora.strftime("%H:%M:%S"),
            "alav": int(alav or 1),
        })
        st.success("Operação adicionada.", icon="✅")

    st.write("Auto-refresh ligado.")

    # --- Tabela (linhas) ---
    # Cabeçalho
    h = ["PAR","SIDE","MODO","ENTRADA","ALVO","PREÇO ATUAL","PNL%","SITUAÇÃO","DATA","HORA","ALAV","EXCLUIR"]
    cols = st.columns([1,1,1.4,1,1,1.2,0.9,1.1,1,0.9,0.8,0.9])
    for c, t in zip(cols, h): c.markdown(f"**{t}**")

    # Linhas
    nova_lista = []
    for idx, op in enumerate(st.session_state.ops_saida):
        c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12 = st.columns([1,1,1.4,1,1,1.2,0.9,1.1,1,0.9,0.8,0.9])

        c1.write(op["par"])
        c2.markdown(
            '<span style="background:{c};color:{tc};padding:2px 8px;border-radius:999px;font-weight:700;">{t}</span>'.format(
                c=("#22C55E" if op["side"]=="LONG" else "#EF4444"),
                tc=("#0B0B0B" if op["side"]=="LONG" else "#fff"),
                t=op["side"]),
            unsafe_allow_html=True
        )
        c3.write(op["modo"])
        c4.write(f"{op['entrada']:.6f}")
        c5.write(f"{op.get('alvo',0.0):.6f}")

        # Preço atual editável
        pa = c6.number_input(
            " ", key=f"pa_{idx}", label_visibility="collapsed",
            value=float(op.get("preco_atual",0.0)), step=0.0001, format="%.6f"
        )
        pnl = _pnl(op["side"], op["entrada"], pa)
        op["preco_atual"] = float(pa)
        op["pnl"] = pnl

        # PNL colorido
        if pnl > 0:
            c7.markdown(f"<span style='color:#22C55E;font-weight:600'>{pnl:.2f}</span>", unsafe_allow_html=True)
        elif pnl < 0:
            c7.markdown(f"<span style='color:#EF4444;font-weight:600'>{pnl:.2f}</span>", unsafe_allow_html=True)
        else:
            c7.write(f"{pnl:.2f}")

        c8.write(op.get("situacao","-"))
        c9.write(op["data"])
        c10.write(op["hora"])
        c11.write(str(op["alav"]))

        if c12.button("Excluir", key=f"del_{idx}", use_container_width=True):
            continue  # pula (exclui)
        nova_lista.append(op)

    st.session_state.ops_saida = nova_lista
