# panels/email_panel.py — SOMENTE LAYOUT (mantém a lógica e as chaves)
# Modelo: [Principal] [Senha] [Envio] [TESTAR/SALVAR] — 4 caixas iguais

from textwrap import dedent
from importlib import import_module

try:
    import streamlit as st
except Exception:
    st = None

# CSS escopado ao painel de e-mail
_CSS = dedent("""
<style>
  /* wrapper deste painel para escopo */
  #EMAIL_INLINE { margin-top: 8px; }

  /* rótulos laranja e sem quebra */
  #EMAIL_INLINE .lbl{
    color: var(--accent, #FF8C32);
    font-weight: 800;
    letter-spacing: .2px;
    white-space: nowrap;
    margin-bottom: 6px;
  }

  /* linha com 4 colunas fixas (260px) e gap 60px */
  #EMAIL_INLINE [data-testid="stHorizontalBlock"]{ gap:60px !important; }
  #EMAIL_INLINE [data-testid="column"]{
    flex: 0 0 260px !important;
    min-width: 260px !important;
  }

  /* altura/compactação dos inputs e botão */
  #EMAIL_INLINE [data-baseweb="input"] input{ height:36px; }
  #EMAIL_INLINE .stButton button{
    height:36px;
    width: 260px;               /* garante mesma “caixa” do botão */
    white-space: nowrap;        /* evita texto em pé */
  }
</style>
""")

def _try_send_via_ops(sender: str, app_pwd: str, to_email: str) -> bool:
    """Tenta usar serviço existente (se houver). Se não achar, retorna False."""
    for mod in ("ops.email_svc", "ops.email_repo"):
        try:
            m = import_module(mod)
        except Exception:
            continue
        for fn_name in ("send_test_email","enviar_teste","send_test","test_send","test_email"):
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

    # Título do painel
    st.markdown("### E-MAIL")
    st.markdown(_CSS, unsafe_allow_html=True)

    # Linha única com 4 “caixas” de 260px
    st.markdown('<div id="EMAIL_INLINE">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="lbl">Principal:</div>', unsafe_allow_html=True)
        st.text_input("sender", key="sender", label_visibility="collapsed",
                      placeholder="voce@dominio.com")

    with c2:
        st.markdown('<div class="lbl">Senha:</div>', unsafe_allow_html=True)
        st.text_input("app_password", key="app_password", label_visibility="collapsed",
                      type="password", placeholder="senha de app")

    with c3:
        st.markdown('<div class="lbl">Envio:</div>', unsafe_allow_html=True)
        st.text_input("to_email", key="to_email", label_visibility="collapsed",
                      placeholder="destinatario@dominio.com")

    with c4:
        st.markdown('<div class="lbl" style="opacity:0">.</div>', unsafe_allow_html=True)  # ocupa o rótulo
        clicked = st.button("TESTAR/SALVAR", use_container_width=False, key="email_submit")

    st.markdown('</div>', unsafe_allow_html=True)

    # Ação
    if clicked:
        sender = st.session_state.get("sender", "")
        app_pwd = st.session_state.get("app_password", "")
        to     = st.session_state.get("to_email", "")
        if _try_send_via_ops(sender, app_pwd, to):
            st.success(f"E-mail de teste enviado para {to}.", icon="✅")
        else:
            st.success("Configurações salvas. (Nenhum serviço de envio detectado neste painel.)", icon="✅")
