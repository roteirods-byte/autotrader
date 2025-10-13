# src/aplicativo.py
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
    TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    TZ = None

import streamlit as st
from services.sheets import get_moedas, save_moedas, _normalize

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO GERAL (deve ser a 1ª chamada do Streamlit)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Interface do projeto — layout aprovado", layout="wide")

# -----------------------------------------------------------------------------
# ESTILO GLOBAL (tema escuro + laranja)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* Laranja do projeto */
:root { --laranja:#f39c12; }

h1, h2, h3, h4 { color: var(--laranja) !important; }

/* Inputs compactos */
.stTextInput>div>div>input, .stPassword>div>div>input { height: 36px; }
.stSelectbox>div>div { min-height: 36px; }
.stButton>button { height: 36px; }

/* Cards de seção */
.caixa { border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; background:#081623; }
.leg { color: var(--laranja); font-weight:600; margin-bottom:6px; }

/* Ajustes das tabs */
.stTabs [data-baseweb="tab-list"] button { font-weight:700; color:#ddd; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--laranja); }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def _agora_ptbr() -> str:
    dt = datetime.now(TZ) if TZ else datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _ok(msg): st.success(msg, icon="✅")
def _warn(msg): st.warning(msg, icon="⚠️")
def _err(msg): st.error(msg, icon="🚫")

# -----------------------------------------------------------------------------
# SEÇÃO: E-MAIL
# -----------------------------------------------------------------------------
def secao_email():
    st.markdown("### Configurações de e-mail")
    with st.container():
        st.markdown('<div class="caixa">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2,2,2,1])

        with c1:
            st.markdown('<div class="leg">Principal</div>', unsafe_allow_html=True)
            mail_user = st.text_input("Principal", key="mail_user",
                                      value=st.session_state.get("mail_user", os.getenv("MAIL_USER","")),
                                      label_visibility="collapsed")
        with c2:
            st.markdown('<div class="leg">Senha (app password)</div>', unsafe_allow_html=True)
            mail_pass = st.text_input("Senha (app password)", type="password", key="mail_pass",
                                      value=st.session_state.get("mail_pass", os.getenv("MAIL_APP_PASSWORD","")),
                                      label_visibility="collapsed")
        with c3:
            st.markdown('<div class="leg">Envio (opcional)</div>', unsafe_allow_html=True)
            mail_to = st.text_input("Envio (opcional)", key="mail_to",
                                    value=st.session_state.get("mail_to", os.getenv("MAIL_TO","")),
                                    label_visibility="collapsed")
        with c4:
            st.write("")  # alinhamento
            testar = st.button("TESTAR/SALVAR", use_container_width=True)

        if testar:
            # salva na sessão
            st.session_state.mail_user = mail_user.strip()
            st.session_state.mail_pass = mail_pass.strip()
            st.session_state.mail_to   = mail_to.strip()

            # testa envio
            try:
                if not (st.session_state.mail_user and st.session_state.mail_pass and st.session_state.mail_to):
                    raise RuntimeError("Preencha Principal, Senha de app e Envio.")
                msg = MIMEText(f"E-mail de teste enviado pela Automação Cripto.\nHorário: {_agora_ptbr()}")
                msg["Subject"] = "Teste — Automação Cripto"
                msg["From"] = st.session_state.mail_user
                msg["To"] = st.session_state.mail_to

                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(st.session_state.mail_user, st.session_state.mail_pass)
                    server.sendmail(st.session_state.mail_user, [st.session_state.mail_to], msg.as_string())

                _ok(f"E-mail de teste enviado via SSL 465 para **{st.session_state.mail_to}**.")
                _warn("Dados salvos nesta sessão. (Se não aparecer, verifique a pasta Spam/Lixo.)")
            except Exception as e:
                _err(f"Falha ao enviar: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SEÇÃO: MOEDAS
# -----------------------------------------------------------------------------
def secao_moedas():
    st.markdown("### PAINEL DE MOEDAS")

    # inicializa lista (lê planilha; cai para lista padrão se falhar)
    if "moedas_lista" not in st.session_state:
        try:
            st.session_state.moedas_lista = get_moedas()
        except Exception as e:
            _warn(f"Não foi possível ler a aba MOEDA da planilha ({e}). Usando lista padrão.")
            st.session_state.moedas_lista = get_moedas()  # já retorna a padrão em caso de erro interno

    with st.container():
        st.markdown('<div class="caixa">', unsafe_allow_html=True)

        # LINHA: input + botão Adicionar
        st.markdown('<div class="leg">Nova:</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([6,1])
        with c1:
            txt_nova = st.text_input("ex.: BTC, ETH, SOL ... (separe por vírgulas)",
                                     key="nova_moeda", label_visibility="collapsed")
        with c2:
            add = st.button("Adicionar", use_container_width=True)

        if add and txt_nova.strip():
            atuais = set(st.session_state.moedas_lista)
            itens = [p.strip() for p in txt_nova.replace(";", ",").split(",") if p.strip()]
            for it in itens:
                norm = _normalize(it)
                if norm:
                    atuais.add(norm)
            st.session_state.moedas_lista = sorted(atuais)
            st.session_state.nova_moeda = ""

        # LINHA: multiselect + Remover
        st.markdown('<div class="leg" style="margin-top:10px;">Selecione para remover</div>', unsafe_allow_html=True)
        c3, c4 = st.columns([6,1])
        with c3:
            to_remove = st.multiselect("", options=st.session_state.moedas_lista, default=[],
                                       key="remover_escolhidas", label_visibility="collapsed")
        with c4:
            rem = st.button("Remover selecionadas", use_container_width=True)

        if rem and to_remove:
            st.session_state.moedas_lista = sorted([m for m in st.session_state.moedas_lista if m not in set(to_remove)])
            st.session_state.remover_escolhidas = []

        # RODAPÉ: salvar/recarregar
        c5, c6 = st.columns([3,3])
        with c5:
            salvar = st.button("Salvar Moedas", use_container_width=True)
        with c6:
            recarregar = st.button("Recarregar da planilha", use_container_width=True)

        if salvar:
            try:
                save_moedas(st.session_state.moedas_lista)
                _ok("Moedas salvas na aba **MOEDA** da planilha.")
            except Exception as e:
                _err(f"Falha ao salvar na planilha: {e}")

        if recarregar:
            try:
                st.session_state.moedas_lista = get_moedas()
                _ok("Lista recarregada da planilha.")
            except Exception as e:
                _err(f"Falha ao recarregar da planilha: {e}")

        st.caption(f"Total: {len(st.session_state.moedas_lista)} pares (ordem alfabética).")
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# OUTRAS SEÇÕES (placeholders no mesmo padrão visual)
# -----------------------------------------------------------------------------
def secao_entrada():
    st.markdown("### Entrada")
    st.info("Espaço reservado para regras de entrada.", icon="🧩")

def secao_saida():
    st.markdown("### Saída")
    st.info("Espaço reservado para monitoramento de saída.", icon="🧭")

def secao_estado():
    st.markdown("### Estado")
    st.info("Painel de estado/diagnóstico.", icon="📊")

# -----------------------------------------------------------------------------
# LAYOUT — TABS SUPERIORES
# -----------------------------------------------------------------------------
st.title("Interface do projeto — layout aprovado")
tabs = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

with tabs[0]: secao_email()
with tabs[1]: secao_moedas()
with tabs[2]: secao_entrada()
with tabs[3]: secao_saida()
with tabs[4]: secao_estado()
