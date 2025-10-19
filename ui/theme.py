# ui/theme.py
from textwrap import dedent

# ==========================
# TOKENS (cores, medidas, raios, sombras, tipografia)
# ==========================
TOKENS = {
    "bg": "#0E1B22",        # Fundo
    "text": "#EAF2F7",      # Texto
    "accent": "#FF8C32",    # Laranja (abas/botões)
    "radius": "12px",
    "shadow": "0 4px 14px rgba(0,0,0,.18)",
    "border_color": "rgba(234,242,247,.10)",
    "border": "1px solid rgba(234,242,247,.10)",
    "font_family": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji"',
    "font_size": "14px",
    "line_height": "1.35",
    "gap_1": "8px",
    "gap_2": "12px",
    "gap_3": "16px",
    "pad": "12px",
}

# Medidas fixas do painel EMAIL
EMAIL_PANEL_SIZE = {
    "width_px": 1306,
    "height_px": 160,
}

def get_tokens() -> dict:
    """Retorna um dict copiável dos tokens (sem lógica)."""
    return dict(TOKENS)

def email_panel_size() -> dict:
    """Retorna as medidas fixas do painel de e-mail (sem lógica)."""
    return dict(EMAIL_PANEL_SIZE)

# ==========================
# THEME CSS (global + EMAIL)
# ==========================
THEME_CSS = dedent(f"""
:root{{
  --bg:{TOKENS['bg']};
  --text:{TOKENS['text']};
  --accent:{TOKENS['accent']};

  --radius:{TOKENS['radius']};
  --shadow:{TOKENS['shadow']};
  --border-color:{TOKENS['border_color']};
  --border:{TOKENS['border']};

  --font-family:{TOKENS['font_family']};
  --font-size:{TOKENS['font_size']};
  --line-height:{TOKENS['line_height']};

  --gap-1:{TOKENS['gap_1']};
  --gap-2:{TOKENS['gap_2']};
  --gap-3:{TOKENS['gap_3']};
  --pad:{TOKENS['pad']};

  --email-w:{EMAIL_PANEL_SIZE['width_px']}px;
  --email-h:{EMAIL_PANEL_SIZE['height_px']}px;
}}

html,body{{height:100%}}
body{{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font-family:var(--font-family);
  font-size:var(--font-size);
  line-height:var(--line-height);
}}
*{{box-sizing:border-box}}

/* Cartão padrão (borda sutil, cantos 12px, sombra leve) */
.panel-card, .card{{
  background:transparent;
  border:var(--border);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  padding:var(--pad);
  color:var(--text);
}}

/* Abas com acento/“orelha” laranja permanente */
.tabs,[role="tablist"]{{
  display:flex;
  gap:var(--gap-2);
  border-bottom:1px solid var(--border-color);
  padding:0 var(--pad) 6px;
}}
.tab,[role="tab"]{{
  position:relative;
  cursor:pointer;
  padding:12px 12px 10px;
  border-bottom:2px solid var(--accent);
  border-top-left-radius:8px;
  border-top-right-radius:8px;
  color:var(--accent); /* laranja permanente */
  text-decoration:none;
}}
.tab::before,[role="tab"]::before{{
  content:"";
  position:absolute;
  top:0; left:10px;
  width:18px; height:8px;
  background:var(--accent);
  border-top-left-radius:6px;
  border-top-right-radius:6px;
}}

/* Botões */
button,.btn{{
  background:transparent;
  color:var(--text);
  border:var(--border);
  border-radius:10px;
  padding:10px 14px;
  box-shadow:var(--shadow);
  cursor:pointer;
}}
.btn.primary{{
  border-color:var(--accent);
  color:var(--accent);
  font-weight:700;
}}
button:focus-visible,.btn:focus-visible{{outline:2px solid var(--accent); outline-offset:2px}}

/* Inputs */
input,select,textarea{{
  background:rgba(255,255,255,.02);
  color:var(--text);
  border:var(--border);
  border-radius:10px;
  padding:10px 12px;
}}
input::placeholder,textarea::placeholder{{color:rgba(234,242,247,.55)}}

/* Labels */
label.label{{opacity:.9; font-weight:600; font-size:12px}}

/* ===== PAINEL ESPECÍFICO: EMAIL (1306 x 160) ===== */
#EMAIL_PANEL, #email-panel, .email-panel, [data-panel="EMAIL"]{{
  width:var(--email-w);
  height:var(--email-h);
  margin:0 auto;
  overflow:hidden;
  display:flex;
  flex-direction:column;
  justify-content:center;
  gap:var(--gap-2);
}}

#EMAIL_PANEL .panel-card,
#email-panel .panel-card,
.email-panel .panel-card,
[data-panel="EMAIL"] .panel-card{{
  height:calc(var(--email-h) - (2 * var(--pad)));
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  gap:var(--gap-2);
  padding:10px var(--pad);
}}

/* Linha de formulário vira GRID: 3 colunas para inputs + 1 para o botão */
#EMAIL_PANEL form,
#email-panel form,
.email-panel form,
[data-panel="EMAIL"] form{{
  display:grid;
  grid-template-columns: 1fr 1fr 1fr auto; /* Remetente | Senha App | Enviar para | Botão */
  align-items:end;          /* alinha verticalmente */
  column-gap:var(--gap-3);
  row-gap:8px;
  margin:0;
}}

#EMAIL_PANEL form > .actions,
#email-panel form > .actions,
.email-panel form > .actions,
[data-panel="EMAIL"] form > .actions{{
  justify-self:end;         /* botão à direita */
  align-self:end;           /* alinhado verticalmente */
  display:flex;
  align-items:center;
}}

#EMAIL_PANEL form > button,
#email-panel form > button,
.email-panel form > button,
[data-panel="EMAIL"] form > button{{
  justify-self:end;         /* se o botão estiver direto no form */
  align-self:end;
}}

#EMAIL_PANEL .field, #email-panel .field, .email-panel .field, [data-panel="EMAIL"] .field{{
  display:flex; flex-direction:column; gap:6px;
}}

/* Alertas opcionais (sucesso/erro) — somente visual */
.alert{{
  display:flex; align-items:center; gap:10px;
  border-radius:10px; padding:8px 10px;
  font-size:12px; line-height:1.2;
  border:1px solid var(--border-color);
  background:rgba(255,255,255,.02);
}}
.alert-success{{ color:#22C55E; border-color:color-mix(in srgb, #22C55E 40%, transparent) }}
.alert-error  {{ color:#EF4444; border-color:color-mix(in srgb, #EF4444 40%, transparent) }}
""")

def get_css() -> str:
    """Retorna o CSS completo do tema (global + EMAIL)."""
    return THEME_CSS

def streamlit_theme() -> dict:
    """
    Retorna o dict de tema do Streamlit (coerente com .streamlit/config.toml).
    Uso opcional. Não altera lógica do app.
    """
    return {
        "base": "dark",
        "primaryColor": TOKENS["accent"],
        "backgroundColor": TOKENS["bg"],
        "secondaryBackgroundColor": TOKENS["bg"],
        "textColor": TOKENS["text"],
    }

def inject_streamlit(st) -> None:
    """
    Injeção opcional de CSS no Streamlit (visual apenas).
    Chame st.markdown(theme.get_css(), unsafe_allow_html=True) no app, se quiser.
    """
    st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)
