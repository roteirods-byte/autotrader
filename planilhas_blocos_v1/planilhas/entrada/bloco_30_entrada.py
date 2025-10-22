# bloco_30_entrada — tabelas Swing (4H) e Posicional (1D) lado a lado
import pandas as pd
import streamlit as st
from planilhas.commons.bloco_00_tokens import COINS

def _table_base():
    return pd.DataFrame({
        "Par": [""],
        "Sinal": ["LONG"],
        "Preço": [0.0],
        "Alvo": [0.0],
        "Ganho %": [0.00],
        "Assertividade %": [0.00],
        "Data": [""],
        "Hora": [""],
    })

def render_entrada_panel():
    st.header("ENTRADA")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Swing (4H)")
        dfA = _table_base()
        st.data_editor(
            dfA, key="entrada_swing",
            column_config={
                "Par": st.column_config.SelectboxColumn("Par", options=COINS),
                "Sinal": st.column_config.SelectboxColumn("Sinal", options=["LONG","SHORT"]),
                "Preço": st.column_config.NumberColumn("Preço", format="%.3f"),
                "Alvo": st.column_config.NumberColumn("Alvo", format="%.3f"),
                "Ganho %": st.column_config.NumberColumn("Ganho %", format="%.2f%%"),
                "Assertividade %": st.column_config.NumberColumn("Assertividade %", format="%.2f%%"),
                "Data": st.column_config.TextColumn("Data"),
                "Hora": st.column_config.TextColumn("Hora"),
            },
            use_container_width=True
        )
    with colB:
        st.subheader("Posicional (1D)")
        dfB = _table_base()
        st.data_editor(
            dfB, key="entrada_posicional",
            column_config={
                "Par": st.column_config.SelectboxColumn("Par", options=COINS),
                "Sinal": st.column_config.SelectboxColumn("Sinal", options=["LONG","SHORT"]),
                "Preço": st.column_config.NumberColumn("Preço", format="%.3f"),
                "Alvo": st.column_config.NumberColumn("Alvo", format="%.3f"),
                "Ganho %": st.column_config.NumberColumn("Ganho %", format="%.2f%%"),
                "Assertividade %": st.column_config.NumberColumn("Assertividade %", format="%.2f%%"),
                "Data": st.column_config.TextColumn("Data"),
                "Hora": st.column_config.TextColumn("Hora"),
            },
            use_container_width=True
        )
# fim bloco_30_entrada
