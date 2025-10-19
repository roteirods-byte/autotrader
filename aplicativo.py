# aplicativo.py
import streamlit as st
from ui.theme import inject_global_css

# Importa o painel de EMAIL (novo). Se faltar, mostra aviso.
try:
    from panels.email_panel import render as email_render
except Exception:
    def email_render():
        st.error("Painel EMAIL não encontrado. Verifique panels/email_panel.py.")

def main():
    st.set_page_config(page_title="Autotrader", page_icon="📈", layout="centered")
    inject_global_css()

    st.markdown("## PAINÉIS DA AUTOMAÇÃO")
    tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["EMAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

    with tab_email:
        email_render()

    # As demais abas permanecem opcionais. Não quebram se ainda não existirem.
    with tab_moedas:
        try:
            from panels.moedas_panel import render as moedas_render
            moedas_render()
        except Exception:
            st.info("Painel MOEDAS em preparação.")

    with tab_entrada:
        try:
            from panels.entrada_panel import render as entrada_render
            entrada_render()
        except Exception:
            st.info("Painel ENTRADA em preparação.")

    with tab_saida:
        try:
            from panels.saida_panel import render as saida_render
            saida_render()
        except Exception:
            st.info("Painel SAÍDA em preparação.")

if __name__ == "__main__":
    main()
