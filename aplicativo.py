# ==============================================
# aplicativo.py  — RESGATE + E-MAIL REVISADO
# ==============================================
import streamlit as st
import ssl, smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------- Fuso horário SP (p/ horário certo no e-mail)
try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    _TZ = None

def _now_sp():
    try:
        return datetime.now(_TZ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------- CONFIGURAÇÃO DA PÁGINA (chamar uma ÚNICA vez e no topo)
st.set_page_config(page_title="Automação Cripto", layout="wide")

# --------- ESTILOS GERAIS
st.markdown("""
<style>
  .orange { color:#ff8c00; font-weight:700; }
  .muted  { opacity:.85; }
  /* inputs mais compactos */
  .email-row .stTextInput > div > div > input {
      padding:6px 10px; font-size:14px; height:38px;
  }
  .email-row .stButton>button { height:40px; font-weight:700; }
  .email-row [data-testid="stTextInput"] { margin-bottom:0.25rem; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# SEÇÃO E-MAIL (revisada — campos em uma linha)
# ==================================================
def _send_test_email(user: str, app_password: str, to_addr: str):
    """Envia e-mail de teste via Gmail (SSL 465)."""
    if not to_addr:
        to_addr = user
    msg = MIMEText(
        f"E-mail de teste enviado pela Automação Cripto.\nHorário: {_now_sp()}"
    )
    msg["Subject"] = "Teste — Automação Cripto"
    msg["From"] = user
    msg["To"] = to_addr

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, app_password)
        server.sendmail(user, [to_addr], msg.as_string())

def secao_email():
    st.subheader("Configurações de e-mail")

    # Valores atuais (mantém os que já estavam na sessão)
    user = st.session_state.get("MAIL_USER", "")
    passwd = st.session_state.get("MAIL_APP_PASSWORD", "")
    to_addr = st.session_state.get("MAIL_TO", "")

    # Três campos + botão, em uma linha
    c1, c2, c3, c4 = st.columns([3, 3, 3, 1.4], gap="small")

    with c1:
        st.markdown("<div class='orange'>Principal</div>", unsafe_allow_html=True)
        user = st.text_input(
            "Principal", value=user, placeholder="seu-email@gmail.com",
            label_visibility="collapsed", key="ui_mail_user",
        )

    with c2:
        st.markdown("<div class='orange'>Senha (app password)</div>", unsafe_allow_html=True)
        passwd = st.text_input(
            "Senha", value=passwd, type="password",
            placeholder="16 dígitos do app password (Google)",
            label_visibility="collapsed", key="ui_mail_pass",
        )

    with c3:
        st.markdown("<div class='orange'>Envio (opcional)</div>", unsafe_allow_html=True)
        to_addr = st.text_input(
            "Envio", value=to_addr, placeholder="para@dominio.com",
            label_visibility="collapsed", key="ui_mail_to",
        )

    with c4:
        st.write("")  # alinhamento
        st.write("")
        acao = st.button("TESTAR/SALVAR", use_container_width=True, key="btn_testar_salvar")

    if acao:
        # Salva na sessão
        st.session_state["MAIL_USER"] = user.strip()
        st.session_state["MAIL_APP_PASSWORD"] = passwd.strip()
        st.session_state["MAIL_TO"] = to_addr.strip()

        # Envia teste para o destinatário (Envio). Se vazio, vai para o Principal.
        try:
            _send_test_email(user.strip(), passwd.strip(), (to_addr or user).strip())
            st.success(f"E-mail de teste enviado via SSL 465 para {(to_addr or user).strip()}.")
            st.info("Dados salvos nesta sessão. (Se não aparecer, verifique a pasta Spam/Lixo.)")
        except Exception as e:
            st.error(f"Falha ao enviar o e-mail de teste: {e}")

# ==================================================
# SEÇÕES DEMAIS (Moedas/Entrada/Saída/Estado)
# → Chamamos se existirem no arquivo; se não, mostramos aviso.
# ==================================================
def _call_if_exists(fn_name: str, titulo: str):
    fn = globals().get(fn_name)
    if callable(fn):
        try:
            fn()
        except Exception as e:
            st.error(f"Erro na seção {titulo}:")
            st.exception(e)
    else:
        st.info(f"Seção **{titulo}** não encontrada (função `{fn_name}()` ausente).")

# =========================
# SEÇÃO: MOEDAS (PAINEL)
# =========================
from typing import List
import streamlit as st

# Importa as funções de planilha (ajustadas no seu services/sheets.py)
try:
    from services.sheets import get_moedas, save_moedas  # get_moedas() -> List[str] (ou [{'PAR': 'BTC'}, ...])
except Exception:
    get_moedas = None
    save_moedas = None

# Fallback com 39 tickers (sem sufixo USDT, em ordem alfabética).
DEFAULT_TICKERS_39: List[str] = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "CRV","DOGE","DOT","ENA","ETC","ETH","FIL","GALA","ICP","IMX",
    "INJ","LDO","LINK","LTC","MANA","MATIC","NEAR","OP","ORDI","PEPE",
    "PYTH","RNDR","RUNE","SEI","SOL","SUI","TON","TRX","UNI"
]

def _normalize_ticker(t: str) -> str:
    """Normaliza o ticker: remove espaços, sufixos e padroniza."""
    t = (t or "").upper().strip()
    t = t.replace("/", "")
    if t.endswith("USDT"):
        t = t[:-4]
    return t

def _load_moedas_na_sessao():
    """Carrega a lista de moedas em st.session_state['moedas']."""
    if "moedas" in st.session_state and isinstance(st.session_state["moedas"], list):
        return

    # Tenta da planilha
    lista = None
    if callable(get_moedas):
        try:
            dados = get_moedas()  # pode retornar ['BTC','ETH',...] OU [{'PAR':'BTC'},...]
            if dados and isinstance(dados, list):
                if isinstance(dados[0], dict):
                    lista = [_normalize_ticker(l.get("PAR", "")) for l in dados]
                else:
                    lista = [_normalize_ticker(x) for x in dados]
        except Exception as e:
            st.warning(f"Não foi possível ler a aba MOEDA da planilha ({e}). Usando lista padrão.")

    if not lista:
        lista = DEFAULT_TICKERS_39.copy()

    # Limpa vazios/duplicados e ordena
    lista = sorted({x for x in lista if x})
    st.session_state["moedas"] = lista

def _salvar_na_planilha(moedas: List[str]):
    """Tenta salvar na planilha, tolerando as duas assinaturas comuns."""
    if not callable(save_moedas):
        st.info("Salvamento em planilha indisponível (save_moedas não encontrado).")
        return False
    try:
        # Algumas versões aceitam list[str]; outras, list[{'PAR': 'BTC'}, ...]
        try:
            save_moedas(moedas)
        except TypeError:
            save_moedas([{"PAR": m} for m in moedas])
        return True
    except Exception as e:
        st.error(f"Falha ao salvar na planilha: {e}")
        return False

def secao_moedas():
    # CSS leve para visual no padrão do projeto
    st.markdown(
        """
        <style>
          .painel-box{border:1px solid rgba(255,255,255,0.15); border-radius:10px; padding:16px; background:#0b1a27;}
          .titulo-laranja{color:#ff8c00; font-weight:700; font-size:1.05rem; letter-spacing:.5px;}
          .mini-label{color:#ff8c00; font-weight:600; margin-bottom:4px; display:block;}
          .stTextInput>div>div>input{height:38px;}
          .stMultiSelect>div>div{min-height:220px; } /* caixa alta para rolar itens selecionáveis */
        </style>
        """,
        unsafe_allow_html=True,
    )

    _load_moedas_na_sessao()
    moedas = st.session_state["moedas"]

    st.markdown('<div class="painel-box">', unsafe_allow_html=True)
    st.markdown('<span class="titulo-laranja">PAINEL DE MOEDAS</span>', unsafe_allow_html=True)
    st.write("")

    # Linha de adicionar
    c1, c2 = st.columns([6, 1.5])
    with c1:
        nova = st.text_input("Nova:", placeholder="ex.: BTC, ETH, SOL ... (separe por vírgulas)")
    with c2:
        if st.button("Adicionar", use_container_width=True):
            adicionados = []
            for raw in (nova or "").split(","):
                t = _normalize_ticker(raw)
                if t and t not in moedas:
                    moedas.append(t)
                    adicionados.append(t)
            if adicionados:
                st.session_state["moedas"] = sorted(moedas)
                st.success(f"Adicionados: {', '.join(adicionados)}")
            else:
                st.info("Nada para adicionar.")

    st.write("")
    # Lista para remover + botão ao lado
    c3, c4 = st.columns([6, 2])
    with c3:
        selecionadas = st.multiselect(
            "Selecione para remover",
            options=st.session_state["moedas"],
            default=[],
            key="rm_moedas"
        )
    with c4:
        if st.button("Remover selecionadas", use_container_width=True):
            if selecionadas:
                st.session_state["moedas"] = sorted([m for m in st.session_state["moedas"] if m not in selecionadas])
                st.warning(f"Removidas: {', '.join(selecionadas)}")
            else:
                st.info("Nenhuma moeda selecionada.")

    st.write("")
    # Ações: salvar / recarregar
    c5, c6 = st.columns([2, 2])
    with c5:
        if st.button("Salvar Moedas", type="primary", use_container_width=True):
            if _salvar_na_planilha(st.session_state["moedas"]):
                st.success("Moedas salvas na planilha.")
    with c6:
        if st.button("Recarregar da planilha", use_container_width=True):
            # Força recarga da planilha sobrescrevendo a sessão
            st.session_state.pop("moedas", None)
            _load_moedas_na_sessao()
            st.success("Recarregado.")

    st.write("")
    st.caption(f"Total: **{len(st.session_state['moedas'])}** pares (ordem alfabética).")
    st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# LAYOUT PRINCIPAL + ABAS
# ==================================================
st.markdown("### <span class='orange'>Interface do projeto — layout aprovado</span>", unsafe_allow_html=True)

abas = st.tabs(["E-mail", "Moedas", "Entrada", "Saída", "Estado"])

with abas[0]:
    secao_email()

with abas[1]:
    _call_if_exists("secao_moedas", "Moedas")

with abas[2]:
    _call_if_exists("secao_entrada", "Entrada")

with abas[3]:
    _call_if_exists("secao_saida", "Saída")

with abas[4]:
    _call_if_exists("secao_estado", "Estado")
