# app.py — esqueleto mínimo (REV7)
import streamlit as st

st.set_page_config(page_title="AUTOMAÇÃO CRIPTO — REV7", layout="wide")

st.title("AUTOMAÇÃO CRIPTO — REV7")
st.caption("Skeleton pronto. Depois trocamos por telas de E-mail, Moedas, Entrada, Saída.")

with st.form("email_form"):
    st.subheader("E-MAIL")
    col1, col2, col3 = st.columns([3,3,3])
    principal = col1.text_input("Principal")
    senha = col2.text_input("Senha (app password)", type="password")
    envio = col3.text_input("Envio")
    enviado = st.form_submit_button("ENVIAR/SALVAR")
    if enviado:
        st.success("OK — dados salvos (stub).")

