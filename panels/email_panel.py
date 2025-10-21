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
  #EMAIL_INLINE [data-baseweb="input"] input{ height:36px; }_
