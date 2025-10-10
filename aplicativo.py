# aplicativo.py — REV8 (layout com abas)
import streamlit as st

st.set_page_config(page_title="AUTOMAÇÃO CRIPTO — REV8", layout="wide")
st.title("AUTOMAÇÃO CRIPTO — REV8")
st.caption("Esqueleto com abas. Depois ligamos E-mail, Moedas, Entrada, Saída.")

abas = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Status"])

# ---- Aba E-mail ----
with abas[0]:
    st.subheader("E-mail")
    with st.form("email_form"):
        col1, col2, col3 = st.columns([3,3,3])
        principal = col1.text_input("Principal")
        senha = col2.text_input("Senha (app password)", type="password")
        envio = col3.text_input("Envio")
        enviado = st.form_submit_button("ENVIAR/SALVAR")
        if enviado:
            st.success("OK — dados salvos (stub).")

# ---- Aba Moedas ----
with abas[1]:
    st.subheader("Moedas")
    st.info("Aqui vamos listar pares, filtros e pesos. (placeholder)")

# ---- Aba Entrada ----
with abas[2]:
    st.subheader("Entrada")
    st.write("Regras de compra/entrada. (placeholder)")
    st.checkbox("Ativar simulação (paper trading)")

# ---- Aba Saída ----
with abas[3]:
    st.subheader("Saída")
    col_a, col_b = st.columns(2)
    col_a.number_input("Take Profit (%)", value=2.0, step=0.1)
    col_b.number_input("Stop Loss (%)", value=1.0, step=0.1)
    st.write("Regras de saída. (placeholder)")

# ---- Aba Status ----
with abas[4]:
    st.subheader("Status")
    st.success("Serviço online e saudável ✅")
    st.code("v0.0.8")
