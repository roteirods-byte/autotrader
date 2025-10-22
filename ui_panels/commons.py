# BLOCO 03 - INICIO (commons.py)
import streamlit as st
from pathlib import Path
from .tokens import APP_TITLE, TITLE_COLOR, EMAIL_W, EMAIL_H

def inject_theme_css():
    css_path = Path(__file__).with_name("theme.css")
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

def page_header():
    st.markdown(f"<h1 style='color:{TITLE_COLOR}'>{APP_TITLE}</h1>", unsafe_allow_html=True)

def section_title(text):
    st.markdown(f"<div class='block-title'>{text}</div>", unsafe_allow_html=True)

def email_container_open():
    st.markdown(
        f"<div class='card' style='width:{EMAIL_W}px; height:{EMAIL_H}px; margin:auto;'>",
        unsafe_allow_html=True
    )

def container_close():
    st.markdown("</div>", unsafe_allow_html=True)
# BLOCO 03 - FIM
