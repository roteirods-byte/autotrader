import streamlit as st
from ui import theme
from panels.email_panel import render_email_panel
from panels.moedas_panel import render_moedas_panel
from panels.entrada_panel import render_entrada_panel
from panels.saida_panel import render_saida_panel

def main():
    st.set_page_config(page_title="Autotrader", page_icon="📈", layout="centered")
    theme.inject_streamlit(st)

    st.markdown("## PAINÉIS DA AUTOMAÇÃO")
    tab_operador, tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(
        ["OPERADOR", "EMAIL", "MOEDAS ✓", "ENTRADA ✓", "SAÍDA ✓"]
    )

    with tab_operador:
        st.info("Painel OPERADOR em preparação.")

    with tab_email:
        render_email_panel()

    with tab_moedas:
        render_moedas_panel()

    with tab_entrada:
        render_entrada_panel()

    with tab_saida:
        render_saida_panel()

if __name__ == "__main__":
    main()
