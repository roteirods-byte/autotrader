import streamlit as st
import pandas as pd

st.set_page_config(page_title="AUTOMAÇÃO CRIPTO", layout="wide")

# Estilização leve para as abas/caixas
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"]{gap:.5rem}
    .stTabs [data-baseweb="tab"]{
        background:rgba(255,255,255,.04);padding:.5rem 1rem;
        border:1px solid rgba(255,255,255,.08);border-radius:8px
    }
    .stTabs [aria-selected="true"]{
        background:rgba(34,211,238,.15);border-color:rgba(34,211,238,.35)
    }
    .metric-box{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
        border-radius:8px;padding:.75rem 1rem}
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
col_ico, col_titulo = st.columns([1,8])
with col_ico: st.write("🧠")
with col_titulo:
    st.title("AUTOMAÇÃO CRIPTO")
    st.caption("Interface do projeto — layout aprovado")

# Estado inicial (sessão)
if "moedas_df" not in st.session_state:
    st.session_state.moedas_df = pd.DataFrame(
        [{"Par":"BTC/USDT","Filtro":"Top10","Peso":1},
         {"Par":"ETH/USDT","Filtro":"Top10","Peso":1}]
    )

# ---------------------- Páginas ----------------------
def page_email():
    st.subheader("Configurações de e-mail")
    with st.form("email_form"):
        c1,c2,c3 = st.columns([3,2,3])
        c1.text_input("Principal", key="email_principal")
        c2.text_input("Senha (app password)", type="password", key="email_senha")
        c3.text_input("Envio (opcional)", key="email_envio")
        ok = st.form_submit_button("ENVIAR / SALVAR")
    if ok:
        st.success("E-mail salvo nesta sessão.")

def page_moedas():
    st.subheader("Moedas / Pares / Filtros / Pesos")
    editado = st.data_editor(
        st.session_state.moedas_df,
        num_rows="dynamic",
        key="moedas_editor",
        use_container_width=True,
        column_config={
            "Par": st.column_config.TextColumn("Par"),
            "Filtro": st.column_config.TextColumn("Filtro"),
            "Peso": st.column_config.NumberColumn("Peso", step=1, min_value=0)
        }
    )
    if st.button("Salvar pares", key="moedas_salvar"):
        st.session_state.moedas_df = editado
        st.success("Pares salvos (sessão).")

def page_entrada():
    st.subheader("Regras de Entrada")
    c1,c2,c3 = st.columns([1,1,1])
    c1.number_input("Risco por trade (%)", min_value=0.0, step=0.1, format="%.2f", key="ent_risco")
    c2.selectbox("Tipo de sinal", ["Cruzamento","Rompimento","RSI","MACD"], key="ent_tipo")
    c3.number_input("Spread máximo (%)", min_value=0.0, step=0.05, format="%.2f", key="ent_spread")

    c4,c5 = st.columns([1,2])
    c4.number_input("Alavancagem", min_value=1, step=1, key="ent_alav")
    c5.text_input("Fonte do sinal (ex.: binance, tradingview)", key="ent_fonte")

    st.number_input("Derrapagem máx. (%)", min_value=0.0, step=0.05, format="%.2f", key="ent_derrap")
    st.info("Espaço reservado para calcular/validar entradas.")

def page_saida():
    st.subheader("Gestão de Saída")
    c1,c2,c3,c4 = st.columns([1,1,1,1])
    c1.number_input("Alvo 1 (%)", min_value=0.0, step=0.1, format="%.2f", key="sai_alvo1")
    c2.number_input("Parada (%)", min_value=0.0, step=0.1, format="%.2f", key="sai_parada")
    c3.selectbox("Modo à direita", ["Desligado","Fixo","Móvel"], key="sai_modo")
    c4.number_input("À direita (%)", min_value=0.0, step=0.05, format="%.2f", key="sai_direita")

    c5,c6 = st.columns([1,1])
    c5.number_input("Alvo 2 (%)", min_value=0.0, step=0.1, format="%.2f", key="sai_alvo2")
    c6.checkbox("Break-even automático", key="sai_be")
    st.info("Aqui depois conectamos a lógica de execução/fechamento.")

def page_estado():
    st.subheader("Estado / Monitor")
    m1,m2,m3 = st.columns(3)
    with m1:
        st.metric("Negociações abertas", 0)
        st.metric("Lucro Hoje", "—")
    with m2:
        st.metric("Saldo", "—")
        st.metric("Exposição", "—")
    with m3:
        st.metric("Sinais pendentes", 0)
        st.metric("Erros", 0)
    st.info("Logs e status em tempo real virão aqui.")

# Navegação (abas)
abas = st.tabs(["E-mail","Moedas","Entrada","Saída","Estado"], key="tabs_main")
with abas[0]: page_email()
with abas[1]: page_moedas()
with abas[2]: page_entrada()
with abas[3]: page_saida()
with abas[4]: page_estado()
