# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Configuração base da página
# ------------------------------------------------------------
st.set_page_config(
    page_title="AUTOMAÇÃO CRIPTO",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------------------------
# Estado inicial (para não perder valores ao navegar nas abas)
# ------------------------------------------------------------
def init_state():
    ss = st.session_state

    # E-mail
    ss.setdefault("email_principal", "")
    ss.setdefault("email_senha_app", "")
    ss.setdefault("email_envio", "")

    # Moedas
    ss.setdefault("moedas_df", pd.DataFrame([
        {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
        {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1},
    ]))

    # Entrada
    ss.setdefault("in_risco", 1.00)
    ss.setdefault("in_tipo_sinal", "Cruzamento")
    ss.setdefault("in_spread", 0.20)
    ss.setdefault("in_alavancagem", 1)
    ss.setdefault("in_fonte", "")
    ss.setdefault("in_slippage", 0.10)

    # Saída
    ss.setdefault("out_alvo1", 1.00)
    ss.setdefault("out_stop", 1.00)
    ss.setdefault("out_modo_direita", "Desligado")
    ss.setdefault("out_direita_pct", 0.50)
    ss.setdefault("out_alvo2", 2.00)
    ss.setdefault("out_breakeven", False)

    # Estado/monitor
    ss.setdefault("montr_abertas", 0)
    ss.setdefault("montr_pendentes", 0)
    ss.setdefault("montr_erros", 0)
    ss.setdefault("montr_lucro_hoje", 0.0)
    ss.setdefault("montr_saldo", None)
    ss.setdefault("montr_exposicao", None)

init_state()

# ------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------
st.markdown("## 🧠 AUTOMAÇÃO CRIPTO")
st.caption("Interface do projeto — layout aprovado")
st.markdown("---")

# ------------------------------------------------------------
# Abas principais
# ------------------------------------------------------------
abas = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

# ------------------------------------------------------------
# PAINEL: E-mail
# ------------------------------------------------------------
with abas[0]:
    st.markdown("### Configurações de e-mail")
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.1, 1, 1])
        with c1:
            st.text_input(
                "Principal",
                key="email_principal",
                placeholder="seu-email@dominio.com",
            )
        with c2:
            st.text_input(
                "Senha (app password)",
                key="email_senha_app",
                type="password",
                placeholder="****************",
            )
        with c3:
            st.text_input(
                "Envio (opcional)",
                key="email_envio",
                placeholder="para@dominio.com",
            )

        st.button("ENVIAR / SALVAR", key="btn_email_salvar")

# ------------------------------------------------------------
# PAINEL: Moedas
# ------------------------------------------------------------
# --- Moedas / Pares / Filtros / Pesos ---
st.subheader("Moedas / Pares / Filtros / Pesos")

if "moedas_df" not in st.session_state:
    st.session_state.moedas_df = pd.DataFrame(
        [{"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
         {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1}]
    )

edited = st.data_editor(
    st.session_state.moedas_df,
    key="moedas_editor",
    use_container_width=True,
    num_rows="dynamic"
)
st.session_state.moedas_df = edited


# ------------------------------------------------------------
# PAINEL: Entrada
# ------------------------------------------------------------
with abas[2]:
    st.markdown("### Regras de Entrada")
    with st.container(border=True):
        r1c1, r1c2, r1c3 = st.columns([1, 1, 1])
        with r1c1:
            st.number_input(
                "Risco por trade (%)",
                min_value=0.0, max_value=100.0, step=0.05,
                key="in_risco", format="%.2f"
            )
        with r1c2:
            st.selectbox(
                "Tipo de sinal",
                ["Cruzamento", "Rompimento", "RSI", "MACD"],
                key="in_tipo_sinal"
            )
        with r1c3:
            st.number_input(
                "Spread máximo (%)",
                min_value=0.0, max_value=5.0, step=0.01,
                key="in_spread", format="%.2f"
            )

        r2c1, r2c2 = st.columns([1, 2])
        with r2c1:
            st.number_input(
                "Alavancagem",
                min_value=1, max_value=125, step=1,
                key="in_alavancagem"
            )
        with r2c2:
            st.text_input(
                "Fonte do sinal (ex.: binance, tradingview)",
                key="in_fonte",
                placeholder=""
            )

        st.number_input(
            "Derrapagem máx. (%)",
            min_value=0.0, max_value=5.0, step=0.01,
            key="in_slippage", format="%.2f"
        )

    st.success("Espaço reservado para calcular/validar entradas.", icon="📈")

# ------------------------------------------------------------
# PAINEL: Saída
# ------------------------------------------------------------
with abas[3]:
    st.markdown("### Gestão de Saída")
    with st.container(border=True):
        s1c1, s1c2, s1c3, s1c4 = st.columns([1, 1, 1, 1])
        with s1c1:
            st.number_input(
                "Alvo 1 (%)",
                min_value=0.0, max_value=100.0, step=0.05,
                key="out_alvo1", format="%.2f"
            )
        with s1c2:
            st.number_input(
                "Parada (%)",
                min_value=0.0, max_value=100.0, step=0.05,
                key="out_stop", format="%.2f"
            )
        with s1c3:
            st.selectbox(
                "Modo à direita",
                ["Desligado", "ATR", "Trailing", "Parcial"],
                key="out_modo_direita"
            )
        with s1c4:
            st.number_input(
                "À direita (%)",
                min_value=0.0, max_value=100.0, step=0.05,
                key="out_direita_pct", format="%.2f"
            )

        s2c1, s2c2 = st.columns([1, 1])
        with s2c1:
            st.number_input(
                "Alvo 2 (%)",
                min_value=0.0, max_value=100.0, step=0.05,
                key="out_alvo2", format="%.2f"
            )
        with s2c2:
            st.checkbox("Break-even automático", key="out_breakeven")

    st.info("Aqui depois conectamos a lógica de execução/fechamento.", icon="🔌")

# ------------------------------------------------------------
# PAINEL: Estado (monitor)
# ------------------------------------------------------------
with abas[4]:
    st.markdown("### Estado / Monitor")
    with st.container(border=True):
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Negociações abertas", st.session_state.montr_abertas)
        m2.metric("Sinais pendentes", st.session_state.montr_pendentes)
        m3.metric("Erros", st.session_state.montr_erros)
        m4.metric("Lucro Hoje", f"{st.session_state.montr_lucro_hoje:.2f}%")
        m5.metric("Saldo", "-" if st.session_state.montr_saldo is None else st.session_state.montr_saldo)
        m6.metric("Exposição", "-" if st.session_state.montr_exposicao is None else st.session_state.montr_exposicao)

    st.caption("Logs e status em tempo real virão aqui.")
