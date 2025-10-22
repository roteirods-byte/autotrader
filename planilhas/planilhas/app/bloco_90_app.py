# bloco_90_app — roteador das 4 planilhas (abas)
import streamlit as st
from planilhas.commons.bloco_01_commons import apply_theme
from planilhas.email.bloco_10_email import render_email_panel
from planilhas.moedas.bloco_20_moedas import render_moedas_panel
from planilhas.entrada.bloco_30_entrada import render_entrada_panel
from planilhas.saida.bloco_40_saida import render_saida_panel
st.set_page_config(page_title="Painéis — Email/Moedas/Entrada/Saída", layout="wide")
apply_theme()
st.markdown("## EMAIL • MOEDAS • ENTRADA • SAÍDA")
tab1, tab2, tab3, tab4 = st.tabs(["EMAIL","MOEDAS","ENTRADA","SAÍDA"])
with tab1: render_email_panel()
with tab2: render_moedas_panel()
with tab3: render_entrada_panel()
with tab4: render_saida_panel()
# fim bloco_90_app
