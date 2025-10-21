# LAYOUT APENAS — não altera a lógica de envio
# Mantém as chaves: sender, app_password, to_email
# Mantém o botão: email_submit
# Exporta: render_email_panel() e render() (compatível com qualquer import)

from textwrap import dedent
try:
    import streamlit as st
except Exception:
    st = None

CSS = dedent("""
<style>
  /* 5) Título geral em laranja (H1/H2) */
  h1, h2 { color:#FF8C32 !important; }

  /* 3) Título da seção “E-MAIL” em laranja */
  .email-title { color:#FF8C32; font-weight:800; margin-bottom:.5rem; }

  /* 2) Linha com 4 caixas — 260px cada + gap 60px */
  #EMAIL_BAR{
    display:flex; align-items:center; gap:60px;
    flex-wrap:wrap; /* se faltar espaço, quebra mantendo medidas */
    margin-top:.25rem;
  }
  #EMAIL_BAR .field{
    width:260px;
  }

  /* 4) Rótulos “Principal/Senha/Envio” em laranja */
  #EMAIL_BAR .lbl{
    color:#FF8C32; font-weight:800; margin-bottom:6px; white-space:nowrap;
  }

  /* Altura padrão dos inputs/botão (só visual) */
  [data-baseweb="input"] input{ height:36px; }
  .stButton button{ height:36px; white-space:nowrap; }
</style>
""")

def _ui():
    if st is None:
        return

    st.markdown(CSS, unsafe_allow_html=True)

    # 3) Muda “CORREIO ELECTRÓNICO” para “E-MAIL”
    st.markdown('<div class="email-title">E-MAIL</div>', unsafe_allow_html=True)

    # 2) Quatro caixas (260px) com gap 60px
    st.markdown('<div id="EMAIL_BAR">', unsafe_allow_html=True)

    # Principal
    st.markdown('<div class="field"><div class="lbl">Principal:</div>', unsafe_allow_html=True)
    st.text_input("sender", key="sender", label_visibility="collapsed", placeholder="voce@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Senha
    st.markdown('<div class="field"><div class="lbl">Senha:</div>', unsafe_allow_html=True)
    st.text_input("app_password", key="app_password", label_visibility="collapsed",
                  type="password", placeholder="senha de app")
    st.markdown('</div>', unsafe_allow_html=True)

    # Envio
    st.markdown('<div class="field"><div class="lbl">Envio:</div>', unsafe_allow_html=True)
    st.text_input("to_email", key="to_email", label_visibility="collapsed",
                  placeholder="destinatario@dominio.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botão (mantém a key usada pela sua lógica)
    st.markdown('<div class="field">', unsafe_allow_html=True)
    st.button("TESTAR/SALVAR", use_container_width=True, key="email_submit")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # fecha EMAIL_BAR

def render_email_panel():
    _ui()

def render():
    _ui()
