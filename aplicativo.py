# aplicativo.py  — SUBSTITUA O ARQUIVO INTEIRO
import streamlit as st
from ui import theme
from panels.email_panel import render_email_panel

def main():
    # Configuração da página
    st.set_page_config(page_title="Autotrader", page_icon="📈", layout="centered")

    # Injetar o visual padrão (cores, medidas, abas, etc.)
    theme.inject_streamlit(st)

    st.markdown("## PAINÉIS DA AUTOMAÇÃO")
    tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["EMAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

    with tab_email:
        # Painel EMAIL no novo padrão visual
        render_email_panel()

    with tab_moedas:
        st.info("Painel MOEDAS em preparação.")

    with tab_entrada:
        st.info("Painel ENTRADA em preparação.")

    with tab_saida:
        st.info("Painel SAÍDA em preparação.")

if __name__ == "__main__":
    main()
