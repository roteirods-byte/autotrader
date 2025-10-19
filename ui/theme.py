# ui/theme.py
import streamlit as st

CSS = """
:root{ --bg:#0b2533; --fg:#e7edf3; --accent:#ff7b1b; }
.stApp, .stApp header { background: var(--bg) !important; }
.stTabs [data-baseweb="tab"] p{ color:var(--fg) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] p{ color:var(--accent) !important; font-weight:700; }
"""

def apply_theme():
    st.set_page_config(page_title="Autotrader", layout="wide")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
