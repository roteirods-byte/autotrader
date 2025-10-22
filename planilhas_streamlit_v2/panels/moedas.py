# BLOCO 20 - INICIO (panels/moedas.py)
import streamlit as st
from services import list_moedas_df, apply_moedas_df

def render():
    st.markdown("<div class='section'>MOEDAS</div>", unsafe_allow_html=True)

    df = list_moedas_df()
    edit = st.data_editor(
        df, use_container_width=True, height=520,
        column_config={
            "Símbolo": st.column_config.TextColumn(width="small"),
            "Nome": st.column_config.TextColumn(),
            "Ativa?": st.column_config.CheckboxColumn(),
            "Observação": st.column_config.TextColumn(),
        },
        hide_index=True
    )
    col1, col2 = st.columns(2)
    if col1.button("Aplicar alterações"):
        apply_moedas_df(edit)
        st.success("Alterações salvas.")
    col2.download_button("Baixar CSV", edit.to_csv(index=False).encode("utf-8"), file_name="moedas.csv")
# BLOCO 20 - FIM
