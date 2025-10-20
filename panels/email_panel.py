# panels/email_panel.py  — SUBSTITUA O ARQUIVO INTEIRO
from textwrap import dedent
try:
    import streamlit as st
except Exception:
    st = None

_LOCAL_CSS = dedent("""
<style>
  /* Área do painel (tamanho fixo) */
  #EMAIL_PANEL{
    width: var(--email-w, 1306px);
    height: var(--email-h, 160px);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--gap-2, 12px);
  }

  /* Estiliza o PRÓPRIO formulário do Streamlit como “card” */
  #EMAIL_PANEL [data-testid="stForm"]{
    background: transparent;
    border: var(--border, 1px solid rgba(234,242,247,.10));
    border-radius: var(--radius, 12px);
    box-shadow: var(--shadow, 0 4px 14px rgba(0,0,0,.18));
    padding: 10px var(--pad, 12px);
    height: calc(var(--email-h, 160px) - (2 * var(--pad, 12px)));
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  /* Grid: 3 campos + coluna do botão */
  #EMAIL_PANEL .grid{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 180px; /* botão com largura fixa */
    column-gap: var(--gap-3, 16px);
    row-gap: 8px;
    align-items: end;
    width: 100%;
  }

  #EMAIL_PANEL .field label{
    font-size: 12px; font-weight: 600; opacity:.9;
    display:block; margin-bottom:6px;
  }

  #EMAIL_PANEL .actions{
    display:flex; align-items:center; justify-content:flex-end;
  }

  /* Não deixar o texto do botão quebrar na vertical */
  #EMAIL_PANEL button{ white-space: nowrap; min-width: 160px; }

  /* Harmoniza input nativo do Streamlit */
  [data-baseweb="input"] input{
    background: rgba(255,255,255,.02) !important;
    color: var(--text, #EAF2F7) !important;
  }

  /* Alertas */
  #EMAIL_PANEL .alert{
    display:flex; align-items:center; gap:10px;
    border-radius:10px; padding:8px 10px;
    font-size:12px; line-height:1.2;
    border:1px solid var(--border-color, rgba(234,242,247,.10));
    background:rgba(255,255,255,.02);
    margin-bottom: 4px;
  }
  #EMAIL_PANEL .alert-success{
    color:#22C55E; border-color: color-mix(in srgb, #22C55E 40%, transparent);
  }
  #EMAIL_PANEL .alert-error{
    color:#EF4444; border-color: color-mix(in srgb, #EF4444 40%, transparent);
  }
</style>
""")

def _flash_messages():
    ss = getattr(st, "session_state", {})
    msg_ok = ss.get("email_success") or ss.get("flash_success")
    msg_er = ss.get("email_error") or ss.get("flash_error")
    return msg_ok, msg_er

def render_email_panel():
    if st is None:
        return

    st.markdown(_LOCAL_CSS, unsafe_allow_html=True)

    # ALERTAS (se existirem mensagens da sua lógica)
    ok, er = _flash_messages()
    with st.container():
        st.markdown('<div id="EMAIL_PANEL">', unsafe_allow_html=True)

        if ok:
            st.markdown(f'<div class="alert alert-success"><strong>Sucesso:</strong> {ok}</div>', unsafe_allow_html=True)
        if er:
            st.markdown(f'<div class="alert alert-error"><strong>Erro:</strong> {er}</div>', unsafe_allow_html=True)

        # FORM VISUAL (a lógica de salvar/enviar continua no seu código)
        with st.form("EMAIL_FORM_VISUAL", clear_on_submit=False):
            st.markdown('<div class="grid">', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([1,1,1,0.0001], gap="medium")  # col4 só posiciona o botão
            defaults = st.session_state
            with col1:
                st.markdown('<div class="field"><label>Remetente</label></div>', unsafe_allow_html=True)
                st.text_input(" ", key="sender", label_visibility="collapsed",
                              value=defaults.get("sender",""), placeholder="voce@dominio.com")
            with col2:
                st.markdown('<div class="field"><label>Senha App</label></div>', unsafe_allow_html=True)
                st.text_input("  ", key="app_password", label_visibility="collapsed",
                              value=defaults.get("app_password",""), type="password", placeholder="senha de app")
            with col3:
                st.markdown('<div class="field"><label>Enviar para</label></div>', unsafe_allow_html=True)
                st.text_input("   ", key="to_email", label_visibility="collapsed",
                              value=defaults.get("to_email",""), placeholder="destinatario@dominio.com")
            with col4:
                st.markdown('<div class="actions">', unsafe_allow_html=True)
                submitted = st.form_submit_button("TESTAR/SALVAR", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Espelhos (se sua lógica usa outros nomes)
        st.session_state["sender_email"] = st.session_state.get("sender","")
        st.session_state["email_app_password"] = st.session_state.get("app_password","")
        st.session_state["email_to"] = st.session_state.get("to_email","")
        st.session_state["email_submit"] = submitted

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__" and st is not None:
    st.set_page_config(layout="centered", page_title="Painel — Email")
    render_email_panel()
