# bloco_10_email — 3 caixas 260px + botão, espaçamento ~40px
import streamlit as st

def render_email_panel():
    st.header("EMAIL")
    col1, sp1, col2, sp2, col3, sp3, col4 = st.columns([13,2,13,2,13,2,10])
    with col1:
        principal = st.text_input("PRINCIPAL")
    with col2:
        senha = st.text_input("SENHA", type="password")
    with col3:
        envio = st.text_input("ENVIO")
    with col4:
        st.write("") ; st.write("")
        salvar = st.button("TESTAR/SALVAR")
    st.caption("Caixas 260px • Espaçamento ~40px • Títulos abóbora")
# fim bloco_10_email
