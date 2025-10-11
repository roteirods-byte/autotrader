# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# -------------------- Config da página --------------------
st.set_page_config(page_title="Automação Cripto", page_icon="🧠", layout="wide")

# -------------------- Estilos (tema escuro + componentes) --------------------
CSS = """
<style>
.stApp { background: #0b1220 !important; }
.block-container { padding-top: 1.2rem; }

h1, h2, h3, h4, h5, h6, p, span, label, div { color: #e6f0ff; }
a { color: #9ad1ff !important; }

.wrapper { margin-top: .5rem; }

.tabs-bar {
  display:flex; gap:.5rem; flex-wrap:wrap; margin:.6rem 0 1.1rem 0;
}

.tab {
  padding:.45rem .85rem;
  border-radius: 999px;
  background:#101a2c;
  border:1px solid rgba(255,255,255,.08);
  color:#cfe4ff;
  font-weight:600; font-size:.92rem;
  cursor:pointer; user-select:none;
}
.tab-active {
  background:#223dee;
  border-color:#2d4bff;
  color:#fff;
}

.card {
  background:#111a2b;
  border:1px solid rgba(255,255,255,.07);
  border-radius:16px;
  padding:18px 18px 8px 18px;
  box-shadow:0 8px 24px rgba(0,0,0,.35);
}

.section-title {
  font-weight:700; font-size:1.05rem; letter-spacing:.2px;
  color:#9ad1ff; margin-bottom:.6rem;
}

/* inputs / selects */
.stTextInput>div>div>input,
.stNumberInput input,
div[data-baseweb="select"] {
  background:#0e1830 !important;
  border:1px solid rgba(255,255,255,.10) !important;
  color:#e6f0ff !important;
}
.stButton>button{
  border-radius:10px; padding:.55rem 1rem;
  background:#223dee; border:1px solid #2d4bff;
}
.stButton>button:hover{ filter:brightness(1.05); }

/* tabela editável */
[data-testid="stDataEditor"]{
  background:#101a2c !important;
  border-radius:12px; border:1px solid rgba(255,255,255,.08);
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -------------------- Cabeçalho --------------------
st.markdown("## 🧠 AUTOMAÇÃO CRIPTO")
st.caption("Interface do projeto — layout aprovado")

# -------------------- Abas (topo) --------------------
# Nota: usamos st.tabs para ficar como seu projeto (abas horizontais)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

# -------------------- E-mail --------------------
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📧 Configurações de e-mail (usaremos App Password)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    email_principal = c1.text_input("Principal", placeholder="seu-email@dominio.com")
    senha_app = c2.text_input("Senha (app password)", type="password")
    email_envio = c3.text_input("Envio (opcional)", placeholder="para@dominio.com")
    st.button("ENVIAR / SALVAR")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Moedas --------------------
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💱 Moedas / Pares / Filtros / Pesos</div>', unsafe_allow_html=True)

    df = pd.DataFrame(
        {"Par": ["BTC/USDT", "ETH/USDT"], "Filtro": ["Top10", "Top10"], "Peso": [1, 1]}
    )
    st.data_editor(
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

# -------------------- Entrada --------------------
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 Regras de Entrada</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    risco = c1.number_input("Risco por trade (%)", value=1.00, step=0.05, min_value=0.0)
    tipo_sinal = c2.selectbox("Tipo de sinal", ["Cruzamento", "Rompimento", "RSI", "MACD"])
    spread_max = c3.number_input("Spread máximo (%)", value=0.20, step=0.05, min_value=0.0)
    derrapagem = c4.number_input("Derrapagem máx. (%)", value=0.10, step=0.05, min_value=0.0)

    c5, c6 = st.columns(2)
    alav = c5.number_input("Alavancagem", value=1, step=1, min_value=1)
    fonte = c6.text_input("Fonte do sinal (ex.: binance, tradingview)")

    st.success("Espaço reservado para calcular/validar entradas.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Saída --------------------
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 Gestão de Saída</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    alvo1 = c1.number_input("Alvo 1 (%)", value=1.00, step=0.10, min_value=0.0)
    parada = c2.number_input("Parada (%)", value=1.00, step=0.10, min_value=0.0)
    modo = c3.selectbox("Modo à direita", ["Desligado", "Parcial", "Total"])
    a_direita = c4.number_input("À direita (%)", value=0.50, step=0.10, min_value=0.0)

    c5, c6 = st.columns(2)
    alvo2 = c5.number_input("Alvo 2 (%)", value=2.00, step=0.10, min_value=0.0)
    breakeven = c6.checkbox("Break-even automático")

    st.info("Aqui depois conectamos a lógica de execução/fechamento.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Estado --------------------
with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Estado / Monitor</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Negociações abertas", "0")
    k2.metric("Sinais pendentes", "0")
    k3.metric("Lucro Hoje", "—")
    k4.metric("Exposição", "—")

    st.caption("Logs e status em tempo real virão aqui.")
    st.markdown('</div>', unsafe_allow_html=True)
