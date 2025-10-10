# Layout base com PAINÉIS no menu lateral (sem abas)
# Painéis: E-mail, Moedas, Entrada, Saída, Estado
import streamlit as st

st.set_page_config(page_title="AUTOMAÇÃO CRIPTO — REV Base", layout="wide")

# --------- Cabeçalho ---------
st.title("AUTOMAÇÃO CRIPTO — REV Base")
st.caption("Esqueleto com painéis. Depois ligamos E-mail, Moedas, Entrada, Saída e Estado.")

# --------- Menu lateral ---------
painel = st.sidebar.radio(
    "Painéis",
    ["E-mail", "Moedas", "Entrada", "Saída", "Estado"],
    index=0
)

# --------- Painel: E-mail ---------
if painel == "E-mail":
    st.subheader("Configurações de E-mail")
    with st.form("email_form"):
        col1, col2, col3 = st.columns([3,3,3])
        principal = col1.text_input("Principal")
        senha = col2.text_input("Senha (app password)", type="password")
        envio = col3.text_input("Envio")
        enviado = st.form_submit_button("ENVIAR / SALVAR")
        if enviado:
            st.success("OK — dados salvos (stub).")

# --------- Painel: Moedas ---------
elif painel == "Moedas":
    st.subheader("Moedas / Pares / Filtros / Pesos")
    st.info("Aqui vamos listar pares, filtros e pesos. (espaço reservado)")

    # editor simples (sem precisar de pandas)
    linhas_iniciais = [
        {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1.0},
        {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1.0},
    ]
    dados = st.data_editor(
        linhas_iniciais,
        num_rows="dynamic",
        use_container_width=True,
        key="ed_moedas"
    )
    st.caption("Você pode adicionar/editar linhas. Depois vamos salvar isso de verdade.")

# --------- Painel: Entrada ---------
elif painel == "Entrada":
    st.subheader("Regras de Entrada")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Risco por trade (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
        st.number_input("Alavancagem", min_value=1, max_value=125, value=1, step=1)
    with col2:
        st.selectbox("Tipo de sinal", ["Cruzamento", "RSI", "MACD", "MME"])
        st.text_input("Fonte do sinal (ex.: binance, tradingview)")
    with col3:
        st.number_input("Spread máximo (%)", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
        st.number_input("Slippage máx. (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.1)
    st.success("Espaço reservado para calcular/validar entradas.")

# --------- Painel: Saída ---------
elif painel == "Saída":
    st.subheader("Gestão de Saída")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Alvo 1 (%)", min_value=0.0, value=1.0, step=0.1)
        st.number_input("Alvo 2 (%)", min_value=0.0, value=2.0, step=0.1)
    with col2:
        st.number_input("Stop (%)", min_value=0.0, value=1.0, step=0.1)
        st.checkbox("Break-even automático")
    with col3:
        st.selectbox("Modo trailing", ["Off", "Simples", "Percentual"])
        st.number_input("Trailing (%)", min_value=0.0, value=0.5, step=0.1)
    st.warning("Aqui depois conectamos a lógica de execução/fechamento.")

# --------- Painel: Estado ---------
elif painel == "Estado":
    st.subheader("Estado / Monitor")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trades abertos", 0)
        st.metric("Lucro Hoje", "—")
    with col2:
        st.metric("Saldo", "—")
        st.metric("Exposição", "—")
    with col3:
        st.metric("Sinais pendentes", 0)
        st.metric("Erros", 0)
    st.info("Logs e status em tempo real virão aqui.")
