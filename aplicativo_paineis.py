# BLOCO 90 - INICIO (aplicativo_paineis.py - navegação lateral)
import streamlit as st
from ui_panels import email, moedas, entrada, saida

st.set_page_config(page_title="Painéis da Automação", layout="wide")

# Navegação simples e estável (sem abas)
opcao = st.sidebar.radio(
    "PAINÉIS",
    ["EMAIL", "MOEDAS", "ENTRADA", "SAÍDA", "OPERADOR"],
    index=0
)

if opcao == "EMAIL":
    email.render()
elif opcao == "MOEDAS":
    moedas.render()
elif opcao == "ENTRADA":
    entrada.render()
elif opcao == "SAÍDA":
    saida.render()
else:
    st.info("Painel OPERADOR em preparação.")
# BLOCO 90 - FIM
