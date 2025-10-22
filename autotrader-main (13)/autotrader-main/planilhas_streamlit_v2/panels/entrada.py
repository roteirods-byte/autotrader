# BLOCO 30 - INICIO (panels/entrada.py)
import streamlit as st
from services import list_entradas_df

def render():
    st.markdown("<div class='section'>ENTRADA</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ENTRADA 4H — SWING")
        df1 = list_entradas_df("SWING")
        st.dataframe(df1, use_container_width=True, height=520)
    with c2:
        st.subheader("ENTRADA 1H — POSICIONAL")
        df2 = list_entradas_df("POSICIONAL")
        st.dataframe(df2, use_container_width=True, height=520)
# BLOCO 30 - FIM
