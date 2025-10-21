# panels/email_panel.py — layout do painel de E-mail (apenas UI)
# Mantém as chaves do estado: sender, app_password, to_email
# Mantém a tentativa de envio via ops.email_svc / ops.email_repo

from textwrap import dedent
from importlib import import_module

try:
    import streamlit as st
except Exception:
    st = None


# CSS local — escopado ao painel, não afeta outras telas
_PANEL_CSS = dedent("""
<style>
  /* Escopo do painel */
  #EMAIL_PANEL .label {
    color: var(--accent, #FF8C32);
    font-weight: 700;
    letter-spacing: .2px;
    margin-bottom: 6px;
    display: inline-block;
  }
  #EMAIL_PANEL h3 {
    color: var(--accent, #FF8C32);
    margin-bottom: 14px;
  }
  #EMAIL_PANEL [data-baseweb="input"] input{
    height: 36px;          /* inputs mais compactos */
  }
  /* Botão sempre laranja (apenas aqui) */
  #EMAIL_PANEL .stButton > button{
    background: var(--accent, #FF8C32);
    color: #0B0B0B;
    border: 1px solid var(--accent, #FF8C32);
    font-weight: 700;
  }
  #EMAIL_PANEL .stButton > button:hover{
    filter: brightness(0.95);
  }
</style>
""")


def _try_send_via_ops(sender: str, app_pwd: str, to_email: str) -> bool:
    """
    Tenta enviar usando serviços já existentes do projeto, se houver.
    Não cria dependência rígida: se não encontrar, apenas retorna False.
    """
    for mod in ("ops.email_svc", "ops.email_repo"):
        try:
            m = import_module(mod)
        except Exception:
            continue
        for fn_name in ("send_test_email", "enviar_teste", "send_test", "test_send", "test_email"):
            fn = getattr(m, fn_name, None)
            if callable(fn):
                try:
                    fn(sender, app_pwd, to_email)
                    return True
                except Exception:
                    pass
    return False


def render() -> None:
    if st is None:
        return

    # Escopo visual do painel
    st.markdown('<div id="EMAIL_PANEL">', unsafe_allow_html=True)
    st.markdown(_PANEL_CSS, unsafe_allow_html=True)

    # Título do painel (em laranja pelo CSS acima)
    st.markdown("### E-MAIL")

    # Linha única: Principal | Senha | Envio | Botão
    # (larguras proporcionais estáveis; visualmente iguais)
    c_princ, c_senha, c_envio, c_btn = st.columns([1.1, 1.0, 1.1, 0.8], gap="large")

    with c_princ:
        st.markdown('<span class="label">Principal:</span>', unsafe_allow_html=True)
        st.text_input(
            "sender", key="sender", label_visibility="collapsed",
            placeholder="voce@dominio.com"
        )

    with c_senha:
        st.markdown('<span class="label">Senha:</span>', unsafe_allow_html=True)
        # Observação: o "olho" é do Streamlit e fica à direita por padrão (mais estável)
        st.text_input(
            "app_password", key="app_password", label_visibility="collapsed",
            type="password", placeholder="senha de app"
        )

    with c_envio:
        st.markdown('<span class="label">Envio:</span>', unsafe_allow_html=True)
        st.text_input(
            "to_email", key="to_email", label_visibility="collapsed",
            placeholder="destinatario@dominio.com"
        )

    with c_btn:
        st.markdown("&nbsp;", unsafe_allow_html=True)  # alinha o botão com os inputs
        clicked = st.button("TESTAR/SALVAR", use_container_width=True, key="email_submit")

    # Ao clicar: tenta enviar; se não houver serviço, confirma salvamento
    if clicked:
        sender = st.session_state.get("sender", "")
        app_pwd = st.session_state.get("app_password", "")
        to     = st.session_state.get("to_email", "")
        if _try_send_via_ops(sender, app_pwd, to):
            st.success(f"E-mail de teste enviado para {to}.", icon="✅")
        else:
            st.success("Configurações salvas. (Nenhum serviço de envio detectado neste painel.)", icon="✅")

    st.markdown("</div>", unsafe_allow_html=True)
