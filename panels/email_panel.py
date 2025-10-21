# LAYOUT APENAS – não altera a lógica de envio
# Mantém as chaves: sender, app_password, to_email
# Exporta: render_email_panel() e render()  (compatível com qualquer import)

from textwrap import dedent
try:
    import streamlit as st
except Exception:
    st = None

_STYLE = dedent("""
<style>
  /* Título geral da página */
  h1 { color: var(--accent, #FF8C32) !important; }

  /* Título da seção E-MAIL */
  .email-title { color: var(--accent, #FF8C32); font-weight: 800; }

  /* Linha com 4 caixas */
  #EMAIL_BAR{
    display:flex; align-items:center; gap:60px;
    margin-top:.25rem;
  }
  #EMAIL_BAR .email-field{ width:260px; }
  #EMAIL_BAR .email-field .lbl{
    color: var(--accent, #FF8C32);
    font-weight:800; letter-spacing:.2px; white-space:nowrap;
    margin-bottom:6px;
  }

  /* inputs e botão */
  [data-baseweb="input"] input{ height:36px; }
  .stButton button{ white-space:nowrap; height:36px; }
</style>
""")

def _render_core():
    if st is None:
        return

    st.markdown(_STYLE, unsafe_allow_html=True)

    # Título da seção
    st.markdown('<div class="email-title">### E-MAIL</div>', unsafe_allow_html=True)

    # Quatro caixas de 260px com gap 60px
    st.markdown('<div id="EMAIL_BAR">', unsafe_allow_html=True)

    # Principal
    st.markdown('<div class="email-field"><div class="lbl">Principal:</div>', unsafe_allow_html=True)
    st.text_input("sender", key="sender", label_visibility="collapsed",
                  placeholder="voce@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Senha
    st.markdown('<div class="email-field"><div class="lbl">Senha:</div>', unsafe_allow_html=True)
    st.text_input("app_password", key="app_password", label_visibility="collapsed",
                  type="password", placeholder="senha de app")
    st.markdown('</div>', unsafe_allow_html=True)

    # Envio
    st.markdown('<div class="email-field"><div class="lbl">Envio:</div>', unsafe_allow_html=True)
    st.text_input("to_email", key="to_email", label_visibility="collapsed",
                  placeholder="destinatario@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botão (mesma key de sempre)
    st.markdown('<div class="email-field">', unsafe_allow_html=True)
    st.button("TESTAR/SALVAR", use_container_width=True, key="email_submit")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_email_panel():
    _render_core()

def render():
    _render_core()
