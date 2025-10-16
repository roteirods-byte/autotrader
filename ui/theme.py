# ui/theme.py
from __future__ import annotations
import os
import streamlit as st

def _default_tokens():
    return {
        "cores": {"laranja": "#ff8c00"},
        "layout": {"input_largura_px": 250, "gap_px": 20},
        "tabela_email": {"largura_px": 1306, "altura_px": 160, "col_narrow_px": 90},
    }

def _load_tokens():
    # Tenta ler YAML; se não houver pyyaml, usa defaults.
    tokens = _default_tokens()
    try:
        import yaml  # type: ignore
        path = os.path.join("ui", "spec.yaml")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                file_tokens = yaml.safe_load(f) or {}
                # merge simples
                for k,v in file_tokens.items():
                    if isinstance(v, dict):
                        tokens.setdefault(k, {}).update(v)
                    else:
                        tokens[k] = v
    except Exception:
        pass
    return tokens

def apply_theme():
    t = _load_tokens()
    st.session_state["__ui_tokens"] = t
    orange   = t["cores"]["laranja"]
    in_w     = t["layout"]["input_largura_px"]
    gap      = t["layout"]["gap_px"]
    tbl_w    = t["tabela_email"]["largura_px"]
    col_narr = t["tabela_email"]["col_narrow_px"]

    css = f"""
    <style>
    :root {{ --orange:{orange}; }}

    /* Títulos principais/abas em abóbora */
    h1, h2, h3.title-orange {{ color: var(--orange) !important; }}
    button[data-baseweb="tab"] p {{ color: var(--orange) !important; font-weight:700; }}
    button[aria-selected="true"] {{ border-bottom:3px solid var(--orange) !important; }}

    /* Rotulos em abóbora */
    .label-orange {{ color: var(--orange); font-weight:700; }}

    /* Inputs lado a lado: gap 20px e largura 250px */
    div[data-testid="stHorizontalBlock"] {{ gap: {gap}px !important; }}
    div[data-testid="stTextInput"] input {{ width: {in_w}px !important; }}

    /* Tabela EMAIL: largura fixa, header laranja e centralizado, colunas estreitas 1 e 2 */
    .email-wrap {{ max-width:{tbl_w}px; width:{tbl_w}px; margin-left:0; }}
    div[data-testid="stElementToolbar"] {{ display:none !important; }} /* some com toolbar */
    div[data-testid="stDataFrame"] thead th {{ color: var(--orange) !important; text-align:center !important; }}
    div[data-testid="stDataFrame"] thead th div {{ justify-content:center !important; }}

    /* 1ª e 2ª colunas (data, hora) mais estreitas */
    div[data-testid="stDataFrame"] tbody td:nth-child(1),
    div[data-testid="stDataFrame"] thead th:nth-child(1) {{ width:{col_narr}px !important; text-align:center; }}
    div[data-testid="stDataFrame"] tbody td:nth-child(2),
    div[data-testid="stDataFrame"] thead th:nth-child(2) {{ width:{col_narr}px !important; text-align:center; }}

    /* Tipografia tabela */
    div[data-testid="stDataFrame"] div[role="grid"]{{ font-size:0.95rem; }}
    .footer-note {{ opacity:.6; font-size:.85rem; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return t
