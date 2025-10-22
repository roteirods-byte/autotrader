# BLOCO 40 - INICIO (panels/saida.py)
import streamlit as st
from services import list_saidas_df

def render():
    st.markdown("<div class='section'>SAÍDA</div>", unsafe_allow_html=True)
    df = list_saidas_df()
    st.dataframe(df, use_container_width=True, height=520)
# BLOCO 40 - FIM
