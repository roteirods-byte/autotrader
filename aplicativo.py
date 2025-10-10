import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- Config da página ----------
st.set_page_config(
    page_title="Automação Cripto",
    page_icon="🧠",
    layout="wide",
)

# ---------- Estilos finos ----------
CUSTOM_CSS = """
<style>
/* tira o rádio lateral do esqueleto antigo, caso ainda exista em cache */
section[data-testid="stSidebar"] div:has(> label:contains("Painéis")) { display:none; }

/* cabeçalho */
.hdr h1 {
  font-weight: 800;
  letter-spacing: .5px;
  margin-bottom: .25rem;
}
.hdr .sub {
  color: #93b3ff;
  font-size: 0.9rem;
}

/* cartões de métrica */
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1rem 1.25rem;
}
.card h4 { margin: 0 0 .35rem 0; font-weight: 700; }
.card .muted { color: #9db4ff; font-size: .85rem; }

/* Tabela */
tbody tr:hover { background: rgba(255,255,255,0.03) !important; }

/* botões */
.stButton>button {
  border-radius: 10px;
  padding: .6rem 1rem;
  font-weight: 700;
}

/* inputs */
.stNumberInput input, .stTextInput input {
  border-radius: 10px;
}

/* tabs no topo mais visíveis */
.stTabs [data-baseweb="tab"] {
  font-weight: 700;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- Estado em memória ----------
if "moedas_df" not in st.session_state:
    st.session_state.moedas_df = pd.DataFrame(
        [
            {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1.0},
            {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1.0},
        ]
    )

# ---------- Cabeçalho ----------
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### 🧠")
with col2:
    st.markdown('<div class="hdr"><h1>AUTOMAÇÃO CRIPTO</h1>'
                '<div class="sub">Interface do projeto — layout aprovado</div></div>',
                unsafe_allow_html=True)

st.divider()

# ---------- Abas principais ----------
tab_email, tab_moedas, tab_entrada, tab_saida, tab_estado = st.tabs(
    ["📧 E-mail", "💱 Moedas", "🎯 Entrada", "🏁 Saída", "📊 Estado"]
)

# --- E-MAIL ---
with tab_email:
    st.write("Configurações de e-mail (usaremos App Password).")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        email_principal = st.text_input("Principal", placeholder="seu-email@dominio.com")
    with c2:
        senha_app = st.text_input("Senha (app password)", type="password")
    with c3:
        destino = st.text_input("Envio (opcional)", placeholder="para@dominio.com")

    if st.button("ENVIAR / SALVAR", type="primary"):
        st.session_state.email_cfg = {
            "principal": email_principal.strip(),
            "senha": senha_app.strip(),
            "envio": destino.strip(),
            "atualizado_em": datetime.utcnow().isoformat()
        }
        st.success("Configurações salvas (em memória por enquanto).")

# --- MOEDAS ---
with tab_moedas:
    st.write("Defina pares, filtros e pesos.")
    st.markdown("> Você pode editar os valores diretamente na tabela abaixo.")

    edited = st.data_editor(
        st.session_state.moedas_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Par": st.column_config.TextColumn("Par", help="Ex.: BTC/USDT"),
            "Filtro": st.column_config.TextColumn("Filtro", help="Ex.: Top10, Vol, etc."),
            "Peso": st.column_config.NumberColumn("Peso", min_value=0.0, max_value=10.0, step=0.1),
        },
    )
    colA, colB = st.columns([1, 3])
    with colA:
        if st.button("Salvar pares/pesos", use_container_width=True):
            st.session_state.moedas_df = edited.copy()
            st.success("Moedas salvas (em memória).")
    with colB:
        st.info("Integração: depois conectamos isto à fonte real (planilha/DB).")

# --- ENTRADA ---
with tab_entrada:
    st.write("Regras de entrada")
    a, b, c = st.columns(3)
    with a:
        risco = st.number_input("Risco por trade (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
        alav = st.number_input("Alavancagem", min_value=1, max_value=125, value=1, step=1)
    with b:
        tipo_sinal = st.selectbox("Tipo de sinal", ["Cruzamento", "Rompimento", "RSI", "MACD"])
        fonte = st.text_input("Fonte do sinal (ex.: binance, tradingview)")
    with c:
        spread = st.number_input("Spread máximo (%)", min_value=0.0, max_value=5.0, value=0.2, step=0.05)
        derrap = st.number_input("Derrapagem máx. (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.05)

    st.markdown('<div class="card"><h4>Validação</h4>'
                '<div class="muted">Espaço reservado para cálculos/validações de entrada.</div></div>',
                unsafe_allow_html=True)

# --- SAÍDA ---
with tab_saida:
    st.write("Gestão de saída")
    a, b, c = st.columns(3)
    with a:
        alvo1 = st.number_input("Alvo 1 (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
        alvo2 = st.number_input("Alvo 2 (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1)
    with b:
        stop = st.number_input("Parada (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
        be = st.checkbox("Break-even automático", value=False)
    with c:
        modo = st.selectbox("Modo à direita", ["Desligado", "Trailing stop", "Parcial"])
        direita = st.number_input("À direita (%)", min_value=0.0, max_value=100.0, value=0.5, step=0.1)

    st.markdown('<div class="card"><h4>Execução</h4>'
                '<div class="muted">Aqui conectaremos a lógica real de fechamento quando a automação estiver plugada.</div></div>',
                unsafe_allow_html=True)

# --- ESTADO ---
with tab_estado:
    st.write("Monitor")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Negociações abertas", 0)
    m2.metric("Sinais pendentes", 0)
    m3.metric("Exposição", "—")
    m4.metric("Lucro Hoje", "—")

    st.markdown('<div class="card"><h4>Logs</h4>'
                '<div class="muted">Logs e status em tempo real virão aqui.</div></div>',
                unsafe_allow_html=True)
