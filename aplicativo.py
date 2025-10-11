import streamlit as st
import pandas as pd

# ========== Config da página ==========
st.set_page_config(page_title="Automação Cripto", layout="wide")

# ========== Estilo (CSS leve) ==========
st.markdown("""
<style>
:root { --primary: #22d3ee; }
h1 { margin-bottom: 0.2rem; }
.subtitle { opacity: .8; margin-bottom: 1rem; }
.card{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}
.section-title{
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

# ========== Cabeçalho ==========
st.markdown("<h1>AUTOMAÇÃO CRIPTO</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Interface do projeto — layout aprovado</div>', unsafe_allow_html=True)

# ========== Abas ==========
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
        key="moedas_editor",
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
    risco = c1.number_input("Risco por trade (%)", value=1.00, step=0.05, format="%.2f", key="risco")
    tipo_sinal = c2.selectbox("Tipo de sinal", ["Cruzamento","Rompimento","RSI","MACD"], key="tipo_sinal")
    spread = c3.number_input("Spread máximo (%)", value=0.20, step=0.05, format="%.2f", key="spread")

    c4, c5 = st.columns([1,1])
    alav = c4.number_input("Alavancagem", value=1, step=1, key="alavancagem")
    fonte = c5.text_input("Fonte do sinal (ex.: binance, tradingview)", key="fonte_sinal")

    c6, _ = st.columns([1,1])
    derrap = c6.number_input("Derrapagem máx. (%)", value=0.10, step=0.05, format="%.2f", key="derrapagem")

    st.markdown('<div class="card" style="margin-top:10px;">'
                'Espaço reservado para calcular/validar entradas.'
                '</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SAÍDA ----------------
with tabs[3]:
    st.markdown('<div class="card"><div class="section-title">Gestão de Saída</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    alvo1   = c1.number_input("Alvo 1 (%)", value=1.00, step=0.05, format="%.2f", key="alvo1")
    parada  = c2.number_input("Parada (%)", value=1.00, step=0.05, format="%.2f", key="parada")
    modo    = c3.selectbox("Modo à direita", ["Desligado","Parcial","Total"], key="modo_direita")
    direita = c4.number_input("À direita (%)", value=0.50, step=0.05, format="%.2f", key="a_direita")

    c5, _ = st.columns([1,1])
    alvo2 = c5.number_input("Alvo 2 (%)", value=2.00, step=0.05, format="%.2f", key="alvo2")
    breakeven = st.checkbox("Break-even automático", value=False, key="breakeven")

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
