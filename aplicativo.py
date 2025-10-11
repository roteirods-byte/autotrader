import streamlit as st
import pandas as pd

st.set_page_config(page_title="AUTOMAÇÃO CRIPTO", page_icon="🧠", layout="wide")

def header(title="AUTOMAÇÃO CRIPTO"):
    st.markdown(
        f"""
        <h1 style="margin-bottom:4px;">{title}</h1>
        <p style="margin-top:-8px;color:#9aa4b2">Interface do projeto — layout aprovado</p>
        """,
        unsafe_allow_html=True,
    )

# Estilos (cores e “cards”)
st.markdown(
    """
    <style>
      .card {background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
             border-radius:10px; padding:16px; margin-bottom:14px;}
      .section-title{font-weight:600;font-size:18px;margin-bottom:6px}
      .muted{color:#9aa4b2}
      .stTabs [data-baseweb="tab-list"] {gap: 8px;}
      .stTabs [data-baseweb="tab"] {background: rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.1);
             padding:8px 14px; border-radius:8px}
      .stTabs [aria-selected="true"] {background: rgba(114,223,222,.15); border-color:#22d3ee}
    </style>
    """,
    unsafe_allow_html=True,
)

header()
tabs = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

# ---------------- E-MAIL ----------------
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Configurações de e-mail</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 3])
    with c1:
        principal = st.text_input("Principal", key="email_principal", placeholder="seu-email@dominio.com")
    with c2:
        senha = st.text_input("Senha (app password)", type="password", key="email_senha")
    with c3:
        envio = st.text_input("Envio (opcional)", key="email_envio", placeholder="para@dominio.com")
    if st.button("ENVIAR / SALVAR", key="btn_salvar_email"):
        st.session_state["email_cfg"] = {"principal": principal, "senha": senha, "envio": envio}
        st.success("Configurações salvas.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MOEDAS ----------------
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Moedas / Pares / Filtros / Pesos</div>', unsafe_allow_html=True)
    default_df = pd.DataFrame(
        [{"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
         {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1}]
    )
    if "moedas_df" not in st.session_state:
        st.session_state["moedas_df"] = default_df.copy()

    st.session_state["moedas_df"] = st.data_editor(
        st.session_state["moedas_df"],
        column_config={
            "Par": st.column_config.TextColumn("Par", help="Ex.: BTC/USDT"),
            "Filtro": st.column_config.SelectboxColumn("Filtro", options=["Top10", "Top20", "Stable", "Manual"]),
            "Peso": st.column_config.NumberColumn("Peso", min_value=0, max_value=10, step=1),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="grid_moedas",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ENTRADA ----------------
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Regras de Entrada</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        risco = st.number_input(
            "Risco por trade (%)", min_value=0.0, max_value=100.0, step=0.1, value=1.0, key="entrada_risco"
        )
    with c2:
        tipo_sinal = st.selectbox(
            "Tipo de sinal", ["Cruzamento", "Rompimento", "RSI", "MACD"], key="entrada_tipo"
        )
    with c3:
        spread = st.number_input(
            "Spread máximo (%)", min_value=0.0, max_value=10.0, step=0.05, value=0.2, key="entrada_spread"
        )

    c4, c5 = st.columns([1, 2])
    with c4:
        alav = st.number_input("Alavancagem", min_value=1, max_value=125, step=1, value=1, key="entrada_alav")
    with c5:
        fonte = st.text_input("Fonte do sinal (ex.: binance, tradingview)", key="entrada_fonte")

    derrap = st.number_input(
        "Derrapagem máx. (%)", min_value=0.0, max_value=5.0, step=0.05, value=0.10, key="entrada_derrap"
    )
    st.info("Espaço reservado para calcular/validar entradas.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SAÍDA ----------------
with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Gestão de Saída</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
    with c1:
        alvo1 = st.number_input("Alvo 1 (%)", min_value=0.0, max_value=50.0, step=0.05, value=1.0, key="saida_alvo1")
    with c2:
        parada = st.number_input("Parada (%)", min_value=0.0, max_value=50.0, step=0.05, value=1.0, key="saida_parada")
    with c3:
        modo = st.selectbox("Modo à direita", ["Desligado", "Agressivo", "Suave"], key="saida_modo")
    with c4:
        direita = st.number_input("À direita (%)", min_value=0.0, max_value=5.0, step=0.05, value=0.5, key="saida_direita")

    c5, c6 = st.columns([2, 1])
    with c5:
        alvo2 = st.number_input("Alvo 2 (%)", min_value=0.0, max_value=100.0, step=0.1, value=2.0, key="saida_alvo2")
    with c6:
        be = st.checkbox("Break-even automático", key="saida_be")

    st.info("Aqui depois conectamos a lógica de execução/fechamento.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ESTADO ----------------
with tabs[4]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Estado / Monitor</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Negociações abertas", 0)
    c2.metric("Saldo", "—")
    c3.metric("Sinais pendentes", 0)
    c4.metric("Erros", 0)
    c5, c6 = st.columns(2)
    with c5:
        st.metric("Lucro Hoje", "—")
    with c6:
        st.metric("Exposição", "—")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><span class="muted">Logs e status em tempo real virão aqui.</span></div>',
                unsafe_allow_html=True)
