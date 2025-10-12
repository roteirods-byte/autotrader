# aplicativo.py
# --- Automação Cripto — layout aprovado -------------------------
# Este arquivo concentra a UI principal (E-mail, Moedas, Entrada, Saída, Estado).
# Persistência das Moedas: usa /data (Render). Se existir services/persist.py, ele é usado;
# caso contrário, caímos num fallback local que salva em /data/moedas.json.

from __future__ import annotations
import os, json
from typing import List, Dict

import pandas as pd
import streamlit as st
# === BLOCO C1 — Tema global (títulos abóbora) ===
import streamlit as st

ORANGE = "#ff8c00"  # abóbora

def aplicar_tema_global():
    st.markdown(f"""
    <style>
      /* Títulos padrão */
      h1, h2, h3, h4 {{ color: {ORANGE} !important; }}

      /* Rótulos dos widgets (compatível com versões recentes do Streamlit) */
      [data-testid="stWidgetLabel"] p,
      .stTextInput label, .stNumberInput label, .stSelectbox label, .stMultiSelect label,
      .stDateInput label, .stCheckbox label, .stRadio label, .stSlider label {{
        color: {ORANGE} !important;
        font-weight: 600 !important;
      }}

      /* Cabeçalhos de tabelas/dataframes */
      thead tr th {{
        color: {ORANGE} !important;
        font-weight: 700 !important;
      }}
    </style>
    """, unsafe_allow_html=True)

# aplicar imediatamente
aplicar_tema_global()
# === FIM BLOCO C1 ===

# ----------------------------------------------------------------
# Persistência (usa services/persist.py se existir; senão, fallback)
# ----------------------------------------------------------------
try:
    from services.persist import load_moedas, save_moedas  # type: ignore
except Exception:
    BASE = os.getenv("DB_PATH", "/data")
    F_MOEDAS = os.path.join(BASE, "moedas.json")

    DEFAULT_MOEDAS = [
        {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
        {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1},
    ]

    def load_moedas() -> List[Dict]:
        try:
            with open(F_MOEDAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_MOEDAS.copy()

    def save_moedas(rows: List[Dict]) -> None:
        os.makedirs(BASE, exist_ok=True)
        with open(F_MOEDAS, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------
# Config da página
# ----------------------------------------------------------------
st.set_page_config(page_title="Automação Cripto", layout="wide")

# ----------------------------------------------------------------
# Helpers de UI
# ----------------------------------------------------------------
def stepper_percent(
    label: str,
    key: str,
    step: float = 0.01,
    min_value: float = 0.0,
    max_value: float | None = None,
    fmt: str = "%.2f",
):
    """Número com botões - / + seguindo o visual aprovado."""
    c1, c2, c3 = st.columns([8, 1, 1])
    val = c1.number_input(
        label, key=key, step=step, min_value=min_value, max_value=max_value, format=fmt
    )
    if c2.button("−", key=f"{key}_menos"):
        st.session_state[key] = max(min_value, round(st.session_state[key] - step, 6))
        st.rerun()
    if c3.button("+", key=f"{key}_mais"):
        new_val = round(st.session_state[key] + step, 6)
        if max_value is None or new_val <= max_value:
            st.session_state[key] = new_val
        st.rerun()
    return st.session_state[key]


def header():
    st.markdown("## 🧠 AUTOMAÇÃO CRIPTO")
    st.caption("Interface do projeto — layout aprovado")
    st.divider()


# ----------------------------------------------------------------
# Seções
# ----------------------------------------------------------------
# --- E-MAIL: formulário e envio real -------------------------
import os, smtplib
from email.message import EmailMessage
import streamlit as st

def _send_test_email(user: str, app_password: str, to_addr: str):
    msg = EmailMessage()
    msg["Subject"] = "Teste - Automação Cripto"
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content("Seu envio de teste está funcionando. 👍")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
        s.ehlo()
        s.starttls()
        s.login(user, app_password)
        s.send_message(msg)

def secao_email():
    st.subheader("Configurações de e-mail")

    # Carrega defaults de variáveis de ambiente (Render)
    default_user = os.getenv("MAIL_USER", "")
    default_to   = os.getenv("MAIL_TO", "")
    # Nunca mostramos nem salvamos a senha em claro
    default_pwd  = os.getenv("MAIL_APP_PASSWORD", "")

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        user = st.text_input("Principal", value=default_user, placeholder="seu-email@dominio.com")
    with col2:
        pwd  = st.text_input("Senha (app password)", value=default_pwd, type="password")
    with col3:
        to   = st.text_input("Envio (opcional)", value=default_to, placeholder="para@dominio.com")

    if st.button("ENVIAR / SALVAR", type="primary"):
        if not user or not pwd:
            st.error("Preencha o e-mail principal e a senha de app.")
            return
        if not to:
            to = user  # se não preencher, envia para o próprio remetente
        try:
            _send_test_email(user, pwd, to)
            st.success("✅ E-mail de teste enviado! Verifique sua caixa de entrada (e o Spam).")
        except smtplib.SMTPAuthenticationError:
            st.error("Falha ao autenticar no Gmail. Confira a senha de app e se a Verificação em 2 etapas está ativada.")
        except Exception as e:
            st.error(f"Não foi possível enviar o e-mail: {e}")


# -----------------------------------------
# Seção: Moedas / Pares / Filtros / Pesos
# -----------------------------------------
import streamlit as st
from services.sheets import get_moedas, save_moedas, seed_moedas
import os

# lista padrão (39) — SEM "USDT" e em ordem alfabética
DEFAULT_COINS_39 = sorted([
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","EGLD","EOS","ETC","FIL","FLOW","FTM","GRT","ICP",
    "INJ","LINK","LTC","MANA","MATIC","NEAR","OP","QNT","SAND","SHIB",
    "SOL","STX","SUI","THETA","TRX","XLM","XRP","XTZ"
])

ORANGE = "#ff8c00"

def secao_moedas():
    st.markdown(f"<h3 style='color:{ORANGE};margin-top:0'>Moedas / Pares / Filtros / Pesos</h3>", unsafe_allow_html=True)

    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        st.error("SHEET_ID não configurado no ambiente da Render.")
        return

    # carrega moedas atuais da planilha (aba MOEDA, col A a partir da linha 2)
    moedas = get_moedas(sheet_id)

    # linha compacta: input + botão lado a lado
    c1, c2 = st.columns([7, 1])
    with c1:
        nova = st.text_input("Nova", placeholder="ex.: BTC, ETH, SOL ...", label_visibility="collapsed")
    with c2:
        if st.button("Adicionar", use_container_width=True):
            if nova:
                # aceita CSV: BTC, ETH, SOL
                novas = [x.strip().upper() for x in nova.split(",") if x.strip()]
                moedas = sorted(set(moedas + novas))
                save_moedas(sheet_id, moedas)
                st.success(f"Adicionado(s): {', '.join(novas)}")
                st.rerun()

    # seletor compacto para remover
    remover = st.multiselect("Selecione para remover", moedas, label_visibility="collapsed")
    c3, c4, c5 = st.columns([2,2,2])
    with c3:
        if st.button("Remover selecionadas", use_container_width=True, disabled=(len(remover)==0)):
            restantes = [m for m in moedas if m not in remover]
            save_moedas(sheet_id, restantes)
            st.success("Removido(s).")
            st.rerun()
    with c4:
        if st.button("Salvar Moedas", use_container_width=True):
            save_moedas(sheet_id, moedas)
            st.success("Salvo.")
    with c5:
        if st.button("Carregar padrão (39)", use_container_width=True, type="secondary"):
            seed_moedas(sheet_id, DEFAULT_COINS_39)
            st.success("Lista padrão (39) carregada.")
            st.rerun()

    st.caption(f"Total: **{len(moedas)}** pares (ordem alfabética)")

    # painel compacto mostrando a lista atual (só para conferência)
    with st.expander("Ver lista atual"):
        st.write(moedas)




def secao_entrada():
    st.subheader("Regras de Entrada")

    # Linha 1
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        stepper_percent("Risco por trade (%)", key="in_risco_pct", step=0.01, min_value=0.0)
    with c2:
        st.selectbox(
            "Tipo de sinal",
            ["Cruzamento", "Rompimento", "RSI", "MACD"],
            key="in_tipo_sinal",
        )
    with c3:
        stepper_percent("Spread máximo (%)", key="in_spread_max", step=0.01, min_value=0.0)

    # Linha 2
    c4, c5 = st.columns([1, 2])
    with c4:
        stepper_percent("Alavancagem", key="in_alavancagem", step=1.0, min_value=1.0, fmt="%.0f")
    with c5:
        st.text_input("Fonte do sinal (ex.: binance, tradingview)", key="in_fonte_sinal")

    # Linha 3
    stepper_percent("Derrapagem máx. (%)", key="in_derrapagem", step=0.01, min_value=0.0)

    st.info("Espaço reservado para calcular/validar entradas.")


def secao_saida():
    st.subheader("Gestão de Saída")

    # Linha 1
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        stepper_percent("Alvo 1 (%)", key="out_alvo1", step=0.01, min_value=0.0)
    with c2:
        stepper_percent("Parada (%)", key="out_stop", step=0.01, min_value=0.0)
    with c3:
        st.selectbox(
            "Modo à direita",
            ["Desligado", "Parcial", "Agressivo"],
            key="out_mode_trailing",
        )
    with c4:
        stepper_percent("À direita (%)", key="out_trailing_pct", step=0.01, min_value=0.0)

    # Linha 2
    c5, _ = st.columns([1, 3])
    with c5:
        st.checkbox("Break-even automático", key="out_break_even")

    stepper_percent("Alvo 2 (%)", key="out_alvo2", step=0.01, min_value=0.0)

    st.info("Aqui depois conectamos a lógica de execução/fechamento.")


def secao_estado():
    st.subheader("Estado / Monitor")

    col = st.columns(6)
    col[0].metric("Negociações abertas", 0)
    col[1].metric("Sinais pendentes", 0)
    col[2].metric("Erros", 0)
    col[3].metric("Lucro Hoje", "—")
    col[4].metric("Saldo", "—")
    col[5].metric("Exposição", "—")

    st.info("Logs e status em tempo real virão aqui.")


# ----------------------------------------------------------------
# App
# ----------------------------------------------------------------
def main():
    # Valores padrão de sessão (evita None/erros)
    st.session_state.setdefault("in_risco_pct", 1.00)
    st.session_state.setdefault("in_spread_max", 0.20)
    st.session_state.setdefault("in_alavancagem", 1.0)
    st.session_state.setdefault("in_fonte_sinal", "")
    st.session_state.setdefault("in_derrapagem", 0.10)
    st.session_state.setdefault("in_tipo_sinal", "Cruzamento")

    st.session_state.setdefault("out_alvo1", 1.00)
    st.session_state.setdefault("out_alvo2", 2.00)
    st.session_state.setdefault("out_stop", 1.00)
    st.session_state.setdefault("out_mode_trailing", "Desligado")
    st.session_state.setdefault("out_trailing_pct", 0.50)
    st.session_state.setdefault("out_break_even", False)

    st.session_state.setdefault("email_principal", "")
    st.session_state.setdefault("email_senha", "")
    st.session_state.setdefault("email_envio", "")

    header()

    tab_email, tab_moedas, tab_entrada, tab_saida, tab_estado = st.tabs(
        ["E-mail", "Moedas", "Entrada", "Saída", "Estado"]
    )

    with tab_email:
        secao_email()
    with tab_moedas:
        secao_moedas()
    with tab_entrada:
        secao_entrada()
    with tab_saida:
        secao_saida()
    with tab_estado:
        secao_estado()


if __name__ == "__main__":
    main()
