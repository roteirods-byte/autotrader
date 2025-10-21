# panels/email_panel.py — layout do painel EMAIL (visual apenas)
# Mantém as mesmas chaves de estado: sender, app_password, to_email.
# Não altera nenhuma lógica de envio/salvamento.

from textwrap import dedent

try:
    import streamlit as st
except Exception:
    st = None

# CSS mínimo para cor do rótulo e compactação
_LOCAL_CSS = dedent("""
<style>
  #EMAIL_ROW .label{
    color: var(--accent, #FF8C32);
    font-weight: 800;
    letter-spacing: .2px;
    white-space: nowrap;
  }
  /* inputs um pouco mais compactos */
  [data-baseweb="input"] input { height: 36px; }
</style>
""")

def render_email_panel() -> None:
    if st is None:
        return

    st.markdown("### E-MAIL")
    st.markdown(_LOCAL_CSS, unsafe_allow_html=True)

    # Uma única linha: Principal | Senha | Envio | Botão
    with st.form("EMAIL_FORM", clear_on_submit=False):
        st.markdown('<div id="EMAIL_ROW">', unsafe_allow_html=True)

        # larguras pensadas para 1366x768 (evita quebra)
        c1,c2,c3,c4,c5,c6,c7 = st.columns([0.7, 2.1, 0.7, 1.9, 0.7, 2.1, 1.0])

        with c1:
            st.markdown('<div class="label">Principal:</div>', unsafe_allow_html=True)
        with c2:
            st.text_input("Remetente", key="sender", label_visibility="collapsed",
                          placeholder="voce@dominio.com")

        with c3:
            st.markdown('<div class="label">Senha:</div>', unsafe_allow_html=True)
        with c4:
            st.text_input("Senha do app (Gmail)", key="app_password",
                          label_visibility="collapsed", type="password",
                          placeholder="senha de app")

        with c5:
            st.markdown('<div class="label">Envio:</div>', unsafe_allow_html=True)
        with c6:
            st.text_input("Enviar para", key="to_email", label_visibility="collapsed",
                          placeholder="destinatario@dominio.com")

        with c7:
            st.form_submit_button("TESTAR/SALVAR", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
