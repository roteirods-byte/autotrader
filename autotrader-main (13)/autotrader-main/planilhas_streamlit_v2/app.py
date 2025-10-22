# BLOCO 90 - INICIO (app.py)
import streamlit as st
from pathlib import Path
from panels import email as email_panel, moedas as moedas_panel, entrada as entrada_panel, saida as saida_panel

st.set_page_config(page_title="Painéis da Automação", layout="wide")

# carrega tema
css = (Path(__file__).with_name("theme.css")).read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.markdown("<h1 class='title'>PAINÉIS DA AUTOMAÇÃO</h1>", unsafe_allow_html=True)

opcao = st.sidebar.radio("PAINÉIS", ["EMAIL", "MOEDAS", "ENTRADA", "SAÍDA"], index=0)

if opcao == "EMAIL":
    email_panel.render()
elif opcao == "MOEDAS":
    moedas_panel.render()
elif opcao == "ENTRADA":
    entrada_panel.render()
else:
    saida_panel.render()
# BLOCO 90 - FIM
