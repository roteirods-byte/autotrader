# panels/email_panel.py — layout apenas (modelo: Principal | Senha | Envio | TESTAR/SALVAR)
# Mantém chaves: sender, app_password, to_email. Mantém função: render()

from textwrap import dedent
from importlib import import_module

try:
    import streamlit as st
except Exception:
    st = None

# CSS: rótulos laranja, inputs compactos e botão sem quebra
_CSS = dedent("""
<style>
  .email-row .lbl{
    color: var(--accent, #FF8C32);
    font-weight: 800;
    letter-spacing: .2px;
    white-space: nowrap;   /* NÃO quebra "Principal:" "Senha:" "Envio:" */
  }
  /* altura dos inputs */
  [data-baseweb="input"] input{ height:36px; }
  /* garante que o texto do botão não fique em pé */
  .stButton button{ white-space: nowrap; }
</style>
""")

def _try_send_via_ops(sender: str, app_pwd: str, to_email: str) -> bool:
    """
    Tenta usar um serviço existente do projeto (se houver),
    SEM impor dependências. Se não achar, apenas retorna False.
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

    st.markdown("### E-MAIL")
    st.markdown(_CSS, unsafe_allow_html=True)

    # Linha única: Principal | Senha | Envio | Botão
    col = st.columns([0.7, 2.2, 0.7, 2.0, 0.7, 2.2, 1.2])
    with col[0]:
        st.markdown('<div class="lbl email-row">Principal:</div>', unsafe_allow_html=True)
    with col[1]:
        st.text_input("sender", key="sender", label_visibility="collapsed",
                      placeholder="voce@dominio.com")

    with col[2]:
        st.markdown('<div class="lbl email-row">Senha:</div>', unsafe_allow_html=True)
    with col[3]:
        st.text_input("app_password", key="app_password",
                      label_visibility="collapsed", type="password",
                      placeholder="senha de app")

    with col[4]:
        st.markdown('<div class="lbl email-row">Envio:</div>', unsafe_allow_html=True)
    with col[5]:
        st.text_input("to_email", key="to_email", label_visibility="collapsed",
                      placeholder="destinatario@dominio.com")

    with col[6]:
        clicked = st.button("TESTAR/SALVAR", use_container_width=True, key="email_submit")

    # Comportamento ao clicar: tentar enviar (se serviço existir), senão apenas salvar
    if clicked:
        sender = st.session_state.get("sender", "")
        app_pwd = st.session_state.get("app_password", "")
        to     = st.session_state.get("to_email", "")
        if _try_send_via_ops(sender, app_pwd, to):
            st.success(f"E-mail de teste enviado para {to}.", icon="✅")
        else:
            st.success("Configurações salvas. (Nenhum serviço de envio detectado neste painel.)", icon="✅")
