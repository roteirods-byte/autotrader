# BLOCO 90 - INICIO (aplicativo_paineis.py - app só dos painéis)
import streamlit as st
from ui_panels import email, moedas, entrada, saida

st.set_page_config(page_title="Painéis da Automação", layout="wide")

# Abas visíveis (clique nelas para trocar de painel)
tabs = st.tabs(["OPERADOR","EMAIL","MOEDAS","ENTRADA","SAÍDA"])
with tabs[0]:
    st.info("Painel OPERADOR em preparação.")
with tabs[1]:
    email.render()
with tabs[2]:
    moedas.render()
with tabs[3]:
    entrada.render()
with tabs[4]:
    saida.render()
# BLOCO 90 - FIM
