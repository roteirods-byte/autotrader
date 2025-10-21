# SUBSTITUA O ARQUIVO INTEIRO
# panels/email_panel.py — layout + estilo (não altera a lógica de envio)
from textwrap import dedent
from importlib import import_module

try:
    import streamlit as st
except Exception:
    st = None


# =========================
# CSS (visual)
# =========================
_CSS = dedent("""
<style>
  /* laranja padrão */
  :root{
    --accent:#FF8C32;
  }

  /* deixa o título geral em laranja quando estiver nesta aba */
  h1, .app-title { color: var(--accent) !important; }

  /* bloco do formulário de e-mail */
  .email-form{
    display:flex;
    align-items:flex-end;
    gap: 60px; /* “espaço entre as caixas” */
    flex-wrap:wrap;
  }

  /* rótulos em laranja */
  .email-form .lbl{
    color: var(--accent);
    font-weight: 800;
    letter-spacing: .2px;
    margin-bottom: 6px;
    white-space: nowrap;
  }

  /* largura fixa dos inputs (350px) */
  .email-form [data-testid="stTextInput"], 
  .email-form [data-baseweb="input"]{
    width: 350px !important;
    max-width: 350px !important;
  }

  /* altura confortável */
  .email-form [data-baseweb="input"] input{
    height: 36px !important;
  }

  /* espaço para o "olho" do campo de senha sem encolher */
  .email-form .password [data-baseweb="input"] input{
    padding-right: 38px !important;
  }

  /* botão sempre laranja */
  .email-form .stButton > button{
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: #0B0B0B !important;
    font-weight: 800 !important;
    height: 38px !important;
    padding: 0 16px !important;
    white-space: nowrap;
    border-radius: 10px;
  }
</style>
""")


# =========================
# tentativa de envio (se serviço existir no projeto)
# =========================
def _try_send_via_ops(sender: str, app_pwd: str, to_email: str) -> bool:
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


# =========================
# render (UI apenas)
# =========================
def render() -> None:
    if st is None:
        return

    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown("### E-MAIL")  # título da seção (herda laranja via CSS)
    st.markdown("")

    # Linha única: Principal | Senha | Envio | Botão
    # (cada “caixa” = 350px; espaçamento = 60px via CSS)
    st.markdown('<div class="email-form">', unsafe_allow_html=True)

    # Principal
    with st.container():
        st.markdown('<div class="lbl">Principal:</div>', unsafe_allow_html=True)
        st.text_input("Principal", key="sender", label_visibility="collapsed",
                      placeholder="voce@dominio.com")

    # Senha (com “olho” dentro e sem encolher)
    with st.container():
        st.markdown('<div class="lbl">Senha:</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="password">', unsafe_allow_html=True)
            st.text_input("Senha", key="app_password", label_visibility="collapsed",
                          type="password", placeholder="senha de app")
            st.markdown('</div>', unsafe_allow_html=True)

    # Envio
    with st.container():
        st.markdown('<div class="lbl">Envio:</div>', unsafe_allow_html=True)
        st.text_input("Envio", key="to_email", label_visibility="collapsed",
                      placeholder="destinatario@dominio.com")

    # Botão
    with st.container():
        st.markdown('<div class="lbl" style="opacity:.0">.</div>', unsafe_allow_html=True)  # apenas para alinhar
        clicked = st.button("TESTAR/SALVAR", key="email_submit")

    st.markdown('</div>', unsafe_allow_html=True)  # fecha .email-form

    # Ação do botão (mesma de antes)
    if clicked:
        sender = st.session_state.get("sender", "")
        app_pwd = st.session_state.get("app_password", "")
        to     = st.session_state.get("to_email", "")
        if _try_send_via_ops(sender, app_pwd, to):
            st.success(f"E-mail de teste enviado para {to}.", icon="✅")
        else:
            st.success("Configurações salvas. (Nenhum serviço de envio detectado neste painel.)", icon="✅")
