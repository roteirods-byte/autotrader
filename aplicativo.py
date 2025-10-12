# ======================================================================
#  Automação Cripto — aplicativo.py (arquivo completo)
#  - Corrige erro do Streamlit: set_page_config chamado 1x e como 1º comando
#  - Tema global (títulos/labels laranja)
#  - Abas: E-mail | Moedas | Entrada | Saída | Estado
#  - Integração com Google Sheets via services.sheets (com try/except)
# ======================================================================

from __future__ import annotations
import os
import time
import traceback
from typing import List

import streamlit as st

# ---------------------- CONFIGURAÇÃO DE PÁGINA (ÚNICA E PRIMEIRA) ----------------------
if "_page_config_done" not in st.session_state:
    st.set_page_config(
        page_title="Automação Cripto",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.session_state["_page_config_done"] = True
# --------------------------------------------------------------------------------------

# ----------------------------- TEMA / ESTILOS (LARANJA) -------------------------------
ORANGE = "#ff8c00"

def _aplicar_tema_global():
    st.markdown(
        f"""
        <style>
          /* Títulos */
          h1, h2, h3, h4, h5, h6 {{
            color: {ORANGE} !important;
          }}

          /* Rótulos dos widgets */
          [data-testid="stWidgetLabel"] p,
          .stTextInput label, .stNumberInput label, .stSelectbox label, .stMultiSelect label,
          .stDateInput label, .stCheckbox label, .stRadio label, .stSlider label {{
            color: {ORANGE} !important;
            font-weight: 600 !important;
          }}

          /* Cabeçalho de tabelas/dataframes */
          thead tr th {{
            color: {ORANGE} !important;
            font-weight: 700 !important;
          }}

          /* Botões primários com destaque sutil */
          button[kind="primary"] {{
            border-color: {ORANGE} !important;
          }}

          /* Cartões/caixas */
          .stAlert > div {{
            border-left: 0.25rem solid {ORANGE};
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_aplicar_tema_global()
# --------------------------------------------------------------------------------------

# ============================= IMPORTS DOS SERVIÇOS (LAZY) =============================
# Evitamos quebrar o app caso o módulo ainda não exista; mostramos msg amigável.
def _import_sheets():
    try:
        from services.sheets import get_moedas, save_moedas  # type: ignore
        return get_moedas, save_moedas
    except Exception as e:
        raise RuntimeError(
            "Não foi possível carregar 'services.sheets'. "
            "Verifique as credenciais (SHEET_ID, GCP_CREDENTIALS_PATH) e o módulo no repositório."
        ) from e

# ======================================================================================
#                                      UTILIDADES
# ======================================================================================
def msg_ok(texto: str):
    st.success(texto, icon="✅")

def msg_erro(texto: str):
    st.error(texto, icon="❌")

def msg_info(texto: str):
    st.info(texto, icon="ℹ️")

# Remoção de sufixo USDT e normalização (ex.: "eth/usdt" -> "ETH")
def _normalize_pair(p: str) -> str:
    p = (p or "").strip().upper().replace(" ", "")
    p = p.replace("/USDT", "").replace("USDT", "")
    return p

# ======================================================================================
#                                     CABEÇALHO
# ======================================================================================
st.title("AUTOMAÇÃO CRIPTO")
st.caption("Interface do projeto — layout aprovado")

# ======================================================================================
#                                      ABAS
# ======================================================================================
abas = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

# --------------------------------------------------------------------------------------
#                                       E-MAIL
# --------------------------------------------------------------------------------------
with abas[0]:
    st.subheader("Configurações de e-mail")

    # Estados salvos em sessão (para não perder após recarregar)
    st.session_state.setdefault("MAIL_USER", "")
    st.session_state.setdefault("MAIL_APP_PASSWORD", "")
    st.session_state.setdefault("MAIL_TO", "")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.session_state["MAIL_USER"] = st.text_input(
            "Principal", value=st.session_state["MAIL_USER"], placeholder="seu-email@dominio.com"
        )
    with col2:
        st.session_state["MAIL_TO"] = st.text_input(
            "Envio (opcional)", value=st.session_state["MAIL_TO"], placeholder="para@dominio.com"
        )

    colp1, colp2 = st.columns([3, 2])
    with colp1:
        st.session_state["MAIL_APP_PASSWORD"] = st.text_input(
            "Senha (app password)", value=st.session_state["MAIL_APP_PASSWORD"], type="password"
        )

    if st.button("ENVIAR / SALVAR", type="primary", use_container_width=False):
        msg_ok("Dados de e-mail armazenados na sessão.")
        # Se desejar persistir em arquivo/planilha, chamar serviço aqui.

# --------------------------------------------------------------------------------------
#                                      MOEDAS
# --------------------------------------------------------------------------------------
with abas[1]:
    st.subheader("Moedas / Pares / Filtros / Pesos")

    # Estado local de moedas
    st.session_state.setdefault("moedas_lista", [])

    # Carregar da planilha (apenas quando usuário pedir)
    def _recarregar_da_planilha():
        try:
            get_moedas, _ = _import_sheets()
            lista = get_moedas()
            # Normaliza, remove duplicadas e ordena
            norm = sorted({ _normalize_pair(x) for x in lista if _normalize_pair(x) })
            st.session_state.moedas_lista = norm
            msg_ok("Recarregado da planilha.")
        except Exception as e:
            msg_erro(f"Falha ao ler do Google Sheets.\n\n{e}")
            st.caption("Dica: confirme SHEET_ID e o caminho de GCP_CREDENTIALS_PATH nas variáveis do Render.")

    def _salvar_em_planilha():
        try:
            _, save_moedas = _import_sheets()
            save_moedas([{"par": p, "filtro": "Top10", "peso": 1} for p in st.session_state.moedas_lista])
            msg_ok("Moedas salvas na planilha.")
        except Exception as e:
            msg_erro(f"Falha ao salvar no Google Sheets.\n\n{e}")

    # Linha de adicionar/remover com campos menores
    c1, c2, c3 = st.columns([5, 1.2, 1.8])
    with c1:
        novos = st.text_input("Nova:", placeholder="ex.: BTC, ETH, SOL...")
    with c2:
        if st.button("Adicionar", use_container_width=True):
            if novos.strip():
                itens = [ _normalize_pair(x) for x in novos.split(",") ]
                itens = [x for x in itens if x]
                base = set(st.session_state.moedas_lista)
                base.update(itens)
                st.session_state.moedas_lista = sorted(base)
            else:
                msg_info("Digite pelo menos um símbolo (ex.: BTC, ETH, SOL).")
    with c3:
        if st.button("Recarregar da planilha", use_container_width=True):
            _recarregar_da_planilha()

    # Lista atual / remover selecionadas
    st.divider()
    st.caption("Selecione para remover")
    selec = st.multiselect("", options=st.session_state.moedas_lista, label_visibility="collapsed")

    c4, c5 = st.columns([1.6, 1.4])
    with c4:
        if st.button("Remover selecionadas", use_container_width=True):
            if selec:
                restante = [x for x in st.session_state.moedas_lista if x not in set(selec)]
                st.session_state.moedas_lista = restante
            else:
                msg_info("Nenhuma moeda selecionada para remover.")
    with c5:
        if st.button("Salvar Moedas", use_container_width=True, type="primary"):
            _salvar_em_planilha()

    st.divider()
    st.caption(f"Total: {len(st.session_state.moedas_lista)} pares (ordem alfabética)")
    # Pequeno "debug" json-condensado
    if st.checkbox("Mostrar lista (debug)"):
        st.json(st.session_state.moedas_lista)

# --------------------------------------------------------------------------------------
#                                      ENTRADA
# --------------------------------------------------------------------------------------
with abas[2]:
    st.subheader("Regras de Entrada")

    colA, colB, colC = st.columns([1, 1, 1])
    with colA:
        risco = st.number_input("Risco por trade (%)", value=1.00, step=0.05, format="%.2f")
        alav = st.number_input("Alavancagem", value=1, step=1, min_value=1)
        derrap = st.number_input("Derrapagem máx. (%)", value=0.10, step=0.05, format="%.2f")
    with colB:
        tipo_sinal = st.selectbox("Tipo de sinal", ["Cruzamento", "Rompimento", "RSI", "MACD"])
        fonte = st.text_input("Fonte do sinal (ex.: binance, tradingview)")
    with colC:
        spread = st.number_input("Spread máximo (%)", value=0.20, step=0.05, format="%.2f")

    st.info("Espaço reservado para calcular/validar entradas.")

# --------------------------------------------------------------------------------------
#                                       SAÍDA
# --------------------------------------------------------------------------------------
with abas[3]:
    st.subheader("Gestão de Saída")

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        alvo1 = st.number_input("Alvo 1 (%)", value=1.00, step=0.10, format="%.2f")
        alvo2 = st.number_input("Alvo 2 (%)", value=2.00, step=0.10, format="%.2f")
    with c2:
        parada = st.number_input("Parada (%)", value=1.00, step=0.10, format="%.2f")
    with c3:
        modo = st.selectbox("Modo à direita", ["Desligado", "Trail %", "Trail ATR"])
    with c4:
        direita = st.number_input("À direita (%)", value=0.50, step=0.05, format="%.2f")

    breakeven = st.checkbox("Break-even automático")
    st.info("Aqui depois conectamos a lógica de execução/fechamento.")

# --------------------------------------------------------------------------------------
#                                       ESTADO
# --------------------------------------------------------------------------------------
with abas[4]:
    st.subheader("Estado / Monitor")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Negociações abertas", value=0)
        st.metric("Lucro Hoje", value="—")
    with c2:
        st.metric("Saldo", value="—")
    with c3:
        st.metric("Sinais pendentes", value=0)
    with c4:
        st.metric("Erros", value=0)

    st.info("Logs e status em tempo real virão aqui.")
