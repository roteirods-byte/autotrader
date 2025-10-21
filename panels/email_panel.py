# panels/email_panel.py — LAYOUT APENAS (mantém funcionamento)
# Mantém as chaves: sender, app_password, to_email
# Mantém o nome esperado pelo app: render_email_panel()

from textwrap import dedent
try:
    import streamlit as st
except Exception:
    st = None

# CSS: 4 “caixas” alinhadas (260px cada) com espaçamento de 60px.
# Títulos e rótulos em laranja (accent). Título geral (h1) também.
_STYLE = dedent("""
<style>
  /* Título geral da página (PAINÉIS DA AUTOMAÇÃO) em laranja */
  h1 { color: var(--accent, #FF8C32) !important; }

  /* Barra do e-mail */
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
  /* inputs mais compactos */
  [data-baseweb="input"] input{ height:36px; }
  .stButton button{ white-space:nowrap; height:36px; }
</style>
""")

def render_email_panel() -> None:
    if st is None:
        return

    st.markdown(_STYLE, unsafe_allow_html=True)

    # Título da seção “E-MAIL” em laranja
    st.markdown('### <span style="color:var(--accent,#FF8C32)">E-MAIL</span>',
                unsafe_allow_html=True)

    # Linha única com 4 caixas (260px) e gap 60px
    st.markdown('<div id="EMAIL_BAR">', unsafe_allow_html=True)

    # Principal
    st.markdown('<div class="email-field"><div class="lbl">Principal:</div>',
                unsafe_allow_html=True)
    st.text_input("sender", key="sender", label_visibility="collapsed",
                  placeholder="voce@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Senha
    st.markdown('<div class="email-field"><div class="lbl">Senha:</div>',
                unsafe_allow_html=True)
    st.text_input("app_password", key="app_password", label_visibility="collapsed",
                  type="password", placeholder="senha de app")
    st.markdown('</div>', unsafe_allow_html=True)

    # Envio
    st.markdown('<div class="email-field"><div class="lbl">Envio:</div>',
                unsafe_allow_html=True)
    st.text_input("to_email", key="to_email", label_visibility="collapsed",
                  placeholder="destinatario@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botão (mantém o comportamento atual do app)
    st.markdown('<div class="email-field">', unsafe_allow_html=True)
    st.button("TESTAR/SALVAR", use_container_width=True, key="email_submit")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
