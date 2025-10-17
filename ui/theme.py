from __future__ import annotations
import streamlit as st


def apply_theme() -> None:
    css = """    <style>
      .main, .stApp { background-color: #0b1e3a; }
      h1, h2, h3, h4 { color: #ffa500 !important; }
      .stDataFrame, .stTable, .stMarkdown, .stText, div, span, p, td, th {
        color: #ffffff !important;
      }
      .panel {
        border: 1px solid #ffffff55; border-radius: 12px; padding: 10px; margin-bottom: 12px;
      }
      .long { color: #00d26a !important; }
      .short { color: #ff4d4f !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
