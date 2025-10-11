# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# ---- CONFIG DA PÁGINA -------------------------------------------------------
st.set_page_config(
    page_title="Automação Cripto",
    page_icon="🧠",
    layout="wide",
)

# ---- TEMA / CSS LEVE --------------------------------------------------------
# (Mantém o dark; ajusta contrastes, cartões e botões)
CSS = """
<style>
/* Fundo e textos */
.stApp { background: #0b1220 !important; }
h1, h2, h3, h4, h5, h6, p, span, label, div { color: #e6f0ff; }

/* Cartões (caixas de seção) */
.block-container { padding-top: 1.5rem; }
.card {
  background: #111a2b;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 18px 18px 8px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}

/* Títulos de seção */
.section-title {
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: .2px;
  color: #9ad1ff;
  margin-bottom: .5rem;
}

/* botões */
.stButton>button {
  border-radius: 10px;
  padding: 0.55rem 1rem;
  background: #223dee;
  border: 1px solid #2d4bff;
}
.stButton>button:hover { filter: brightness(1.05); }

/* inputs */
.stTextInput>div>div>input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
  background: #0e1830 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #e6f0ff !important;
}

/* tabela editável */
[data-testid="stDataEditor"] {
  background: #101a2c !important;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.06);
}

/* “chips” pequenos de métrica */
.kpi {
  background:#101a2c;
  border:1px solid rgba(255,255,255,0.06);
  padding:.9rem 1rem;
  border-radius:14px;
}
.kpi h3 { margin:0; font-size: .95rem; color:#9ad1ff; }
.kpi .big { font-size: 1.4rem; font-weight: 700; margin-top:.25rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---- CABEÇALHO --------------------------------------------------------------
st.markdown("### 🧠 **AUTOMAÇÃO CRIPTO**")
st.caption("Interface do projeto — layout aprovado")

# ---- SIDEBAR (PAINÉIS) ------------------------------------------------------
with st.sidebar:
    st.markdown("#### Painéis")
    painel = st.radio(
        " ",
        options=["E-mail", "Moedas", "Entrada", "Saída", "Estado"],
        index=0,
        label_visibility="collapsed",
    )

# ---- E-MAIL -----------------------------------------------------------------
if painel == "E-mail":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📧 Configurações de e-mail (usaremos App Password)</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.4, 1, 1.2])
    with col1:
        email_principal = st.text_input("Principal", placeholder="seu-email@dominio.com")
    with col2:
        senha_app = st.text_input("Senha (app password)", type="password")
    with col3:
        email_envio = st.text_input("Envio (opcional)", placeholder="para@dominio.com")
    st.button("ENVIAR / SALVAR")
    st.markdown('</div>', unsafe_allow_html=True)

# ---- MOEDAS -----------------------------------------------------------------
elif painel == "Moedas":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💱 Moedas / Pares / Filtros / Pesos</div>', unsafe_allow_html=True)

    # Tabela editável (exemplo; depois ligamos à sua fonte)
    df = pd.DataFrame(
        {
            "Par": ["BTC/USDT", "ETH/USDT"],
            "Filtro": ["Top10", "Top10"],
            "Peso": [1, 1],
        }
    )
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Par": st.column_config.TextColumn(width="medium"),
            "Filtro": st.column_config.TextColumn(width="small"),
            "Peso": st.column_config.NumberColumn(min_value=0, step=1, width="small"),
        },
    )
    st.caption("Você pode adicionar/editar linhas. Depois conectamos isso ao armazenamento real.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---- ENTRADA ----------------------------------------------------------------
elif painel == "Entrada":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 Regras de Entrada</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        risco = st.number_input("Risco por trade (%)", value=1.00, step=0.05, min_value=0.0)
    with c2:
        tipo_sinal = st.selectbox("Tipo de sinal", ["Cruzamento", "Rompimento", "RSI", "MACD"])
    with c3:
        spread_max = st.number_input("Spread máximo (%)", value=0.20, step=0.05, min_value=0.0)
    with c4:
        derrapagem = st.number_input("Derrapagem máx. (%)", value=0.10, step=0.05, min_value=0.0)

    c5, c6 = st.columns(2)
    with c5:
        alav = st.number_input("Alavancagem", value=1, step=1, min_value=1)
    with c6:
        fonte = st.text_input("Fonte do sinal (ex.: binance, tradingview)")

    st.success("Espaço reservado para calcular/validar entradas.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---- SAÍDA ------------------------------------------------------------------
elif painel == "Saída":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 Gestão de Saída</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        alvo1 = st.number_input("Alvo 1 (%)", value=1.00, step=0.10, min_value=0.0)
    with c2:
        parada = st.number_input("Parada (%)", value=1.00, step=0.10, min_value=0.0)
    with c3:
        modo = st.selectbox("Modo à direita", ["Desligado", "Parcial", "Total"])
    with c4:
        a_direita = st.number_input("À direita (%)", value=0.50, step=0.10, min_value=0.0)

    c5, c6 = st.columns(2)
    with c5:
        alvo2 = st.number_input("Alvo 2 (%)", value=2.00, step=0.10, min_value=0.0)
    with c6:
        breakeven = st.checkbox("Break-even automático")

    st.info("Aqui depois conectamos a lógica de execução/fechamento.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---- ESTADO -----------------------------------------------------------------
elif painel == "Estado":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Estado / Monitor</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<div class="kpi"><h3>Negociações abertas</h3><div class="big">0</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi"><h3>Sinais pendentes</h3><div class="big">0</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi"><h3>Lucro Hoje</h3><div class="big">—</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="kpi"><h3>Exposição</h3><div class="big">—</div></div>', unsafe_allow_html=True)

    st.caption("Logs e status em tempo real virão aqui.")
    st.markdown('</div>', unsafe_allow_html=True)
