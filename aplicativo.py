# ======================================================================
#  Automação Cripto — aplicativo.py (arquivo completo, rev. compacta)
#  Mudanças:
#   - Inputs da aba E-mail muito menores (≈240–260px)
#   - Envio robusto (SSL 465 → fallback TLS 587) e envia para 2 destinos:
#     destinatário + Gmail principal (cópia)
#   - Mensagens de sucesso/erro mais claras
# ======================================================================

from __future__ import annotations
import os
import time
import traceback
from typing import List

import streamlit as st

# E-mail
import smtplib
from email.message import EmailMessage

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
          /* Títulos e guias */
          h1, h2, h3, h4, h5, h6 {{ color: {ORANGE} !important; }}
          [data-testid="stWidgetLabel"] p,
          .stTextInput label, .stPassword label, .stNumberInput label, .stSelectbox label,
          .stMultiSelect label, .stCheckbox label {{ color: {ORANGE} !important; font-weight:600; }}
          .stTabs [data-baseweb="tab"] p {{ color:{ORANGE} !important; font-weight:700 !important; }}
          .stTabs [data-baseweb="tab"][aria-selected="true"] p {{ border-bottom:2px solid {ORANGE}; }}

          /* Cabeçalho de tabelas */
          thead tr th {{ color:{ORANGE} !important; font-weight:700 !important; }}

          /* Alertas com filete laranja */
          .stAlert > div {{ border-left:0.25rem solid {ORANGE}; }}

          /* ------- Inputs BEM MENORES apenas na seção de e-mail ------- */
          #email-box div[data-testid="stTextInput"],
          #email-box div[data-testid="stPassword"] {{
            display:inline-block !important;
            width: 260px !important;
            max-width: 260px !important;
          }}
          #email-box div[data-testid="stTextInput"] input,
          #email-box div[data-testid="stPassword"] input {{
            width: 240px !important;
            max-width: 240px !important;
            padding: 6px 10px !important;
          }}
          /* segunda coluna (Envio opcional) também compacta */
          #email-box .col-envio div[data-testid="stTextInput"] {{
            width: 300px !important; max-width:300px !important;
          }}
          #email-box .col-envio div[data-testid="stTextInput"] input {{
            width: 280px !important; max-width:280px !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

_aplicar_tema_global()
# --------------------------------------------------------------------------------------

# ============================= IMPORTS DOS SERVIÇOS (LAZY) =============================
def _import_sheets():
    try:
        from services.sheets import get_moedas, save_moedas  # type: ignore
        return get_moedas, save_moedas
    except Exception as e:
        raise RuntimeError(
            "Não foi possível carregar 'services.sheets'. "
            "Verifique as credenciais (SHEET_ID, GCP_CREDENTIALS_PATH) e o módulo."
        ) from e

# ======================================================================================
#                                      UTILIDADES
# ======================================================================================
def msg_ok(texto: str): st.success(texto, icon="✅")
def msg_erro(texto: str): st.error(texto, icon="❌")
def msg_info(texto: str): st.info(texto, icon="ℹ️")

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

    st.session_state.setdefault("MAIL_USER", "")
    st.session_state.setdefault("MAIL_APP_PASSWORD", "")
    st.session_state.setdefault("MAIL_TO", "")

    st.markdown('<div id="email-box">', unsafe_allow_html=True)

    col1, spacer, col2 = st.columns([1, 0.1, 1])
    with col1:
        st.session_state["MAIL_USER"] = st.text_input(
            "Principal",
            value=st.session_state["MAIL_USER"],
            placeholder="seu-email@gmail.com",
        )
        st.session_state["MAIL_APP_PASSWORD"] = st.text_input(
            "Senha (app password)",
            value=st.session_state["MAIL_APP_PASSWORD"],
            type="password",
        )
    with col2:
        st.markdown('<div class="col-envio">', unsafe_allow_html=True)
        st.session_state["MAIL_TO"] = st.text_input(
            "Envio (opcional)",
            value=st.session_state["MAIL_TO"],
            placeholder="destinatario@dominio.com",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------- Envio real de e-mail + salvamento ----------------------
    def _enviar_email_teste(user: str, app_pw: str, para: str | None) -> tuple[list[str], str]:
        """
        Envia e-mail de teste via Gmail.
        Retorna (lista_destinatários_efetivos, rota_usada).
        Além do 'para' informado, envia cópia ao próprio 'user'.
        """
        if not user or not app_pw:
            raise ValueError("Preencha o e-mail principal e a senha (app password).")

        destino = para.strip() if para and para.strip() else user
        to_list = list({destino, user})  # garante cópia para o Gmail principal

        msg = EmailMessage()
        msg["Subject"] = "Teste — Automação Cripto"
        msg["From"] = user
        msg["To"] = destino
        if user != destino:
            msg["Cc"] = user
        msg.set_content(
            f"Olá!\n\nE-mail de teste enviado pela Automação Cripto.\n"
            f"Horário: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Se chegou, o envio está OK."
        )

        # 1) SSL 465
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=25) as smtp:
                smtp.login(user, app_pw)
                smtp.send_message(msg, from_addr=user, to_addrs=to_list)
            return to_list, "SSL 465"
        except Exception as e_ssl:
            # 2) fallback TLS 587
            try:
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=25) as smtp:
                    smtp.ehlo(); smtp.starttls(); smtp.ehlo()
                    smtp.login(user, app_pw)
                    smtp.send_message(msg, from_addr=user, to_addrs=to_list)
                return to_list, "TLS 587"
            except Exception as e_tls:
                raise RuntimeError(
                    "Falha nos dois métodos (SSL:465 e TLS:587).\n\n"
                    f"Erro SSL: {e_ssl}\n\nErro TLS: {e_tls}"
                )

    if st.button("ENVIAR / SALVAR", type="primary"):
        user = (st.session_state["MAIL_USER"] or "").strip()
        app_pw = (st.session_state["MAIL_APP_PASSWORD"] or "").strip()
        para = (st.session_state["MAIL_TO"] or "").strip()

        msg_ok("Dados de e-mail armazenados na sessão.")
        try:
            destinatarios, rota = _enviar_email_teste(user, app_pw, para)
            msg_ok(f"E-mail de teste enviado via **{rota}** para: {', '.join(destinatarios)}.")
            st.caption("Obs.: verifique também Spam/Lixo (Hotmail/Outlook costuma segurar testes).")
        except Exception as e:
            msg_erro(
                "Falha ao enviar. Confirme **App Password** (senha de app) do Gmail, "
                "verificação em 2 etapas e o e-mail principal."
            )
            with st.expander("Detalhes técnicos"):
                st.code("".join(traceback.format_exception_only(type(e), e)))

    st.caption(
        "Para Gmail é **obrigatório** usar *App Password* (senha de app). "
        "Conta → Segurança → Verificação em duas etapas → Senhas de app."
    )

# --------------------------------------------------------------------------------------
#                                      MOEDAS
# --------------------------------------------------------------------------------------
with abas[1]:
    st.subheader("Moedas / Pares / Filtros / Pesos")

    st.session_state.setdefault("moedas_lista", [])

    def _import_sheets_guard():
        try:
            return _import_sheets()
        except Exception as e:
            msg_erro(f"Sheets indisponível. {e}")
            return None, None

    def _recarregar_da_planilha():
        get_moedas, _ = _import_sheets_guard()
        if not get_moedas: return
        try:
            lista = get_moedas()
            norm = sorted({_normalize_pair(x) for x in lista if _normalize_pair(x)})
            st.session_state.moedas_lista = norm
            msg_ok("Recarregado da planilha.")
        except Exception as e:
            msg_erro(f"Falha ao ler do Google Sheets.\n\n{e}")

    def _salvar_em_planilha():
        _, save_moedas = _import_sheets_guard()
        if not save_moedas: return
        try:
            payload = [{"par": p, "filtro": "Top10", "peso": 1} for p in st.session_state.moedas_lista]
            save_moedas(payload)
            msg_ok("Moedas salvas na planilha.")
        except Exception as e:
            msg_erro(f"Falha ao salvar no Google Sheets.\n\n{e}")

    c1, c2, c3 = st.columns([5, 1.2, 1.8])
    with c1:
        novos = st.text_input("Nova:", placeholder="ex.: BTC, ETH, SOL...")
    with c2:
        if st.button("Adicionar", use_container_width=True):
            if novos.strip():
                itens = [_normalize_pair(x) for x in novos.split(",")]
                itens = [x for x in itens if x]
                base = set(st.session_state.moedas_lista); base.update(itens)
                st.session_state.moedas_lista = sorted(base)
            else:
                msg_info("Digite pelo menos um símbolo.")
    with c3:
        if st.button("Recarregar da planilha", use_container_width=True):
            _recarregar_da_planilha()

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
                msg_info("Nenhuma moeda selecionada.")
    with c5:
        if st.button("Salvar Moedas", use_container_width=True, type="primary"):
            _salvar_em_planilha()

    st.divider()
    st.caption(f"Total: {len(st.session_state.moedas_lista)} pares (ordem alfabética)")
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
    c1, c2, c3, c4 = st.columns(4)
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
