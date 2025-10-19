# ui/theme.py
import streamlit as st

PRIMARY = "#0b2533"
BG_DARK = "#08202B"
FG = "#e7edf3"
ACCENT = "#ff7b1b"

def inject_global_css():
    st.markdown(
        f"""
        <style>
          body {{ background:{BG_DARK}; color:{FG}; }}
          .stTabs [data-baseweb="tab"] p {{ color:{ACCENT} !important; font-weight:700; }}
          .stTabs [aria-selected="true"] {{ border-color:{ACCENT} !important; }}
          .email-panel {{ width:1306px; height:160px; background:{BG_DARK};
                         border:2px solid #ffffff; border-radius:8px; padding:16px; }}
          .email-row {{ display:flex; gap:50px; align-items:center; }}
          .email-row .fxw input {{ width:250px !important; }}
          .email-row .btn250 button {{ width:250px !important; height:40px;
                                      background:{ACCENT} !important; color:{PRIMARY} !important; font-weight:700; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
