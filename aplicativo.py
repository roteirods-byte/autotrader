# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# -------------------- Config da página --------------------
st.set_page_config(page_title="Automação Cripto", page_icon="🧠", layout="wide")
# ===== Cabeçalho =====
st.markdown("<h1>AUTOMAÇÃO CRIPTO</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Interface do projeto — layout aprovado</div>', unsafe_allow_html=True)
st.write("")

# ===== Abas no topo =====
tabs = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

# ---------------- E-MAIL ----------------
with tabs[0]:
    st.markdown('<div class="card"><div class="section-title">Configurações de e-mail</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1.5, 2])
    email_principal = c1.text_input("Principal", key="email_principal", placeholder="seu-email@dominio.com")
    email_senha = c2.text_input("Senha (app password)", key="email_senha", type="password")
    email_envio = c3.text_input("Envio (opcional)", key="email_envio", placeholder="para@dominio.com")
    st.button("ENVIAR / SALVAR", key="btn_email")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MOEDAS ----------------
with tabs[1]:
    st.markdown('<div class="card"><div class="section-title">Moedas / Pares / Filtros / Pesos</div>', unsafe_allow_html=True)
    if "moedas_df" not in st.session_state:
        st.session_state.moedas_df = pd.DataFrame({
            "Par":    ["BTC/USDT", "ETH/USDT"],
            "Filtro": ["Top10",     "Top10"],
            "Peso":   [1,            1]
        })
    st.data_editor(
        st.session_state.moedas_df,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Par":    st.column_config.TextColumn("Par", width="medium"),
            "Filtro": st.column_config.SelectboxColumn("Filtro", options=["Top10","Top20","Custom"]),
            "Peso":   st.column_config.NumberColumn("Peso", min_value=0, step=1, format="%d"),
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ENTRADA ----------------
with tabs[2]:
    st.markdown('<div class="card"><div class="section-title">Regras de Entrada</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    risco = c1.number_input("Risco por trade (%)", value=1.00, step=0.05, format="%.2f")
    tipo_sinal = c2.selectbox("Tipo de sinal", ["Cruzamento","Rompimento","RSI","MACD"])
    spread = c3.number_input("Spread máximo (%)", value=0.20, step=0.05, format="%.2f")

    c4, c5 = st.columns([1,1])
    alav = c4.number_input("Alavancagem", value=1, step=1)
    fonte = c5.text_input("Fonte do sinal (ex.: binance, tradingview)")

    c6, c7 = st.columns([1,1])
    derr = c6.number_input("Derrapagem máx. (%)", value=0.10, step=0.05, format="%.2f")

    st.markdown('<div class="card" style="margin-top:10px;">'
                'Espaço reservado para calcular/validar entradas.'
                '</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SAÍDA ----------------
with tabs[3]:
    st.markdown('<div class="card"><div class="section-title">Gestão de Saída</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    alvo1 = c1.number_input("Alvo 1 (%)", value=1.00, step=0.05, format="%.2f")
    parada = c2.number_input("Parada (%)", value=1.00, step=0.05, format="%.2f")
    modo  = c3.selectbox("Modo à direita", ["Desligado","Parcial","Total"])
    direita = c4.number_input("À direita (%)", value=0.50, step=0.05, format="%.2f")

    c5, c6 = st.columns([1,1])
    alvo2 = c5.number_input("Alvo 2 (%)", value=2.00, step=0.05, format="%.2f")
    breakeven = c6.checkbox("Break-even automático", value=False)

    st.markdown('<div class="card" style="margin-top:10px;">'
                'Aqui depois conectamos a lógica de execução/fechamento.'
                '</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ESTADO ----------------
with tabs[4]:
    st.markdown('<div class="card"><div class="section-title">Estado / Monitor</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Negociações abertas", 0)
    m2.metric("Saldo", "—")
    m3.metric("Sinais pendentes", 0)
    m4.metric("Erros", 0)

    m5, m6 = st.columns(2)
    m5.metric("Lucro Hoje", "—")
    m6.metric("Exposição", "—")

    st.markdown('<div class="card" style="margin-top:10px;">'
                'Logs e status em tempo real virão aqui.'
                '</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Estilos (tema escuro + componentes) --------------------
CSS = """
<style>
/* Fundo e layout */
.stApp { background:#0b1220 !important; }
.block-container { padding-top: 1rem; max-width: 1200px; }

/* Tipografia */
h1,h2,h3,h4,h5,h6,p,span,label,div { color:#e6f0ff; }
.caption, .stCaption, small { color:#9ab6d9 !important; }

/* Cabeçalho */
h2 { font-weight: 800; letter-spacing:.3px; }
.subtitle { margin-top:-6px; color:#89a5c9; }

/* Abas no TOPO com cara de “seu projeto” */
.stTabs [data-baseweb="tab-list"]{
  border-bottom:1px solid rgba(255,255,255,.08);
  gap:.5rem; padding-bottom:.4rem; margin:.2rem 0 1rem 0;
}
.stTabs [data-baseweb="tab"]{
  background:#101a2c; color:#cfe4ff;
  border:1px solid rgba(255,255,255,.10);
  border-radius:10px; padding:.45rem .85rem; font-weight:600;
}
.stTabs [data-baseweb="tab"]:hover{ filter:brightness(1.05); }
.stTabs [aria-selected="true"]{
  background:#223dee; border-color:#2d4bff; color:#fff;
}

/* Cards (seções) */
.card{
  background:#0f1a2e;
  border:1px solid rgba(255,255,255,.08);
  border-radius:16px; padding:18px 18px 8px 18px;
  box-shadow:0 8px 24px rgba(0,0,0,.35);
}
.section-title{ color:#9ad1ff; font-weight:700; margin-bottom:.6rem; }

/* Inputs / botões */
.stTextInput>div>div>input,
.stNumberInput input,
div[data-baseweb="select"]{
  background:#0e1830 !important;
  border:1px solid rgba(255,255,255,.12) !important;
  color:#e6f0ff !important;
}
.stButton>button{
  background:#223dee; border:1px solid #2d4bff; color:#fff;
  border-radius:10px; padding:.55rem 1rem; font-weight:700;
}
.stButton>button:hover{ filter:brightness(1.07); }

/* Tabela editável */
[data-testid="stDataEditor"]{
  background:#101a2c !important;
  border-radius:12px; border:1px solid rgba(255,255,255,.08);
}

/* Métricas (Estado) */
[data-testid="stMetric"]{
  background:#0f1a2e; border:1px solid rgba(255,255,255,.08);
  border-radius:12px; padding:10px;
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
