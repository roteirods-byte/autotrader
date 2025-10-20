import streamlit as st
from ui import theme
from panels.email_panel import render_email_panel
from panels.moedas_panel import render_moedas_panel  # << usa o painel de moedas

def main():
    st.set_page_config(page_title="Autotrader", page_icon="📈", layout="centered")
    theme.inject_streamlit(st)

    st.markdown("## PAINÉIS DA AUTOMAÇÃO")
    tab_operador, tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(
        ["OPERADOR", "EMAIL", "MOEDAS ✓", "ENTRADA", "SAÍDA"]
    )

    with tab_operador:
        st.info("Painel OPERADOR em preparação.")

    with tab_email:
        render_email_panel()

    with tab_moedas:
        render_moedas_panel()   # << NÃO deixa mensagem “em preparação”

    with tab_entrada:
        st.info("Painel ENTRADA em preparação.")

    with tab_saida:
        st.info("Painel SAÍDA em preparação.")

if __name__ == "__main__":
    main()
