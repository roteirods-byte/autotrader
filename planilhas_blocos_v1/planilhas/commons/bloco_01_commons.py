# bloco_01_commons — utilitários de tema/formatos/data-hora
import datetime, pytz, streamlit as st
from .bloco_00_tokens import COLORS, SIZES

TZ = pytz.timezone("America/Sao_Paulo")

def now_date() -> str:
    return datetime.datetime.now(TZ).strftime("%Y-%m-%d")

def now_time() -> str:
    return datetime.datetime.now(TZ).strftime("%H:%M:%S")

def apply_theme():
    css = f"""
    <style>
      .stApp {{ background: {COLORS['BG']}; color: {COLORS['TEXT']}; }}
      h1,h2,h3,h4,h5 {{ color: {COLORS['TITLE']} !important; }}
      .metric-green {{ color: {COLORS['LONG']} !important; }}
      .metric-red {{ color: {COLORS['SHORT']} !important; }}
      /* inputs 260px em desktops comuns */
      [data-testid="stTextInput"] input {{
         max-width: {SIZES['INPUT_W']}px;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# fim bloco_01_commons
