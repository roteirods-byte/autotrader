# bloco_20_moedas — editor das 39 moedas (ordem A–Z)
import pandas as pd
import streamlit as st
from planilhas.commons.bloco_00_tokens import COINS

def render_moedas_panel():
    st.header("MOEDAS")
    df = pd.DataFrame({"Moeda": sorted(COINS), "Ativa": [True]*len(COINS)})
    st.data_editor(
        df, key="moedas_editor", num_rows="fixed",
        column_config={
            "Moeda": st.column_config.TextColumn("Moeda", disabled=True),
            "Ativa": st.column_config.CheckboxColumn("Ativa")
        },
        use_container_width=True
    )
# fim bloco_20_moedas
