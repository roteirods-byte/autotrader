# BLOCO 90 - INICIO (aplicativo_paineis.py - app só dos painéis)
import streamlit as st
from ui_panels import email, moedas, entrada, saida

st.set_page_config(page_title="Painéis da Automação", layout="wide")

tab_oper, tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(
    ["OPERADOR","EMAIL","MOEDAS","ENTRADA","SAÍDA"]
)

with tab_oper:
    st.info("Painel OPERADOR em preparação.")
with tab_email:
    email.render()
with tab_moedas:
    moedas.render()
with tab_entrada:
    entrada.render()
with tab_saida:
    saida.render()
# BLOCO 90 - FIM
