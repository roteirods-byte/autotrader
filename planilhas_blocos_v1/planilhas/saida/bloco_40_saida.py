# bloco_40_saida — tabela de saída com exclusão de linha
import pandas as pd
import streamlit as st
from planilhas.commons.bloco_00_tokens import COINS

def render_saida_panel():
    st.header("SAÍDA")
    df = pd.DataFrame({
        "Moeda": [""],
        "Side": ["LONG"],
        "Modo": ["Swing"],
        "Entrada": [0.0],
        "Preço Atual": [0.0],
        "Alvo": [0.0],
        "PNL %": [0.00],
        "Situação": [""],
        "Data": [""],
        "Hora": [""],
        "Excluir": [False],
    })
    st.data_editor(
        df, key="saida_editor",
        column_config={
            "Moeda": st.column_config.SelectboxColumn("Moeda", options=COINS),
            "Side": st.column_config.SelectboxColumn("Side", options=["LONG","SHORT"]),
            "Modo": st.column_config.SelectboxColumn("Modo", options=["Swing","Posicional"]),
            "Entrada": st.column_config.NumberColumn("Entrada", format="%.3f"),
            "Preço Atual": st.column_config.NumberColumn("Preço Atual", format="%.3f"),
            "Alvo": st.column_config.NumberColumn("Alvo", format="%.3f"),
            "PNL %": st.column_config.NumberColumn("PNL %", format="%.2f%%"),
            "Situação": st.column_config.TextColumn("Situação"),
            "Data": st.column_config.TextColumn("Data"),
            "Hora": st.column_config.TextColumn("Hora"),
            "Excluir": st.column_config.CheckboxColumn("Excluir"),
        },
        use_container_width=True
    )
# fim bloco_40_saida
