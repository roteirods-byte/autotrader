import streamlit as st

def main():
    # Deve ser a 1ª chamada do app
    st.set_page_config(page_title="Autotrader", page_icon="📈", layout="centered")

    st.markdown("## PAINÉIS DA AUTOMAÇÃO")
    tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["EMAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

    with tab_email:
        # Import tardio evita erros de configuração/duplicação
        from panels.email_panel import render as email_render
        email_render()

    with tab_moedas:
        st.info("Painel MOEDAS em preparação.")

    with tab_entrada:
        st.info("Painel ENTRADA em preparação.")

    with tab_saida:
        st.info("Painel SAÍDA em preparação.")

if __name__ == "__main__":
    main()
