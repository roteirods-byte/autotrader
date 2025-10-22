# BLOCO 20 - INICIO (moedas.py)
import streamlit as st
import pandas as pd
from . import tokens as T
from .commons import inject_theme_css, page_header, section_title

def init_state():
    if T.SS_COINS not in st.session_state:
        st.session_state[T.SS_COINS] = pd.DataFrame({
            "Símbolo": T.DEFAULT_SYMBOLS,
            "Nome": ["" for _ in T.DEFAULT_SYMBOLS],
            "Ativo?": [True for _ in T.DEFAULT_SYMBOLS],
            "Observação": ["" for _ in T.DEFAULT_SYMBOLS],
        })

def render():
    inject_theme_css()
    page_header()
    section_title("MOEDAS")
    init_state()
    df = st.session_state[T.SS_COINS]

    with st.container():
        c1,c2,c3 = st.columns([1.2,2,1])
        novo_sym = c1.text_input("Novo símbolo", placeholder="ex.: ABC")
        novo_nome = c2.text_input("Nome da moeda", placeholder="Nome (opcional)")
        add = c3.button("Adicionar", use_container_width=True)
        if add and novo_sym:
            if novo_sym.upper() not in df["Símbolo"].values:
                new_row = {"Símbolo": novo_sym.upper(), "Nome": novo_nome, "Ativo?": True, "Observação": ""}
                st.session_state[T.SS_COINS] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

    st.caption("Buscar (símbolo ou nome)")
    filtro = st.text_input("", placeholder="Digite para filtrar...")
    df_view = st.session_state[T.SS_COINS]
    if filtro:
        f = filtro.lower()
        df_view = df_view[df_view["Símbolo"].str.lower().str.contains(f) | df_view["Nome"].str.lower().str.contains(f)]

    edit_df = st.data_editor(
        df_view,
        use_container_width=True,
        height=480,
        column_config={
            "Símbolo": st.column_config.TextColumn(width="small"),
            "Nome": st.column_config.TextColumn(),
            "Ativo?": st.column_config.CheckboxColumn(),
            "Observação": st.column_config.TextColumn()
        },
        hide_index=True
    )

    cA, cB = st.columns([1,1])
    with cA:
        if st.button("Aplicar alterações"):
            base = st.session_state[T.SS_COINS].set_index("Símbolo")
            edited = edit_df.set_index("Símbolo")
            base.update(edited)
            st.session_state[T.SS_COINS] = base.reset_index()
            st.success("Alterações aplicadas.")
    with cB:
        st.download_button("Baixar CSV", st.session_state[T.SS_COINS].to_csv(index=False).encode("utf-8"), file_name="moedas.csv")
# BLOCO 20 - FIM
