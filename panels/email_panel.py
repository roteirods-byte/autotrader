# panels/email_panel.py
# SUBSTITUA O ARQUIVO INTEIRO
# Visual do Painel de E-mail — mantém a lógica intacta (apenas UI)
# - Cartão 1306x160
# - Abas com “orelhas” laranja permanentes (decorativas)
# - Mensagens de sucesso/erro compatíveis com o restante do tema
#
# Observação:
# • Não altera funções de envio/salvamento. Este arquivo apenas desenha o painel.
# • Os valores e o estado continuam em st.session_state com as mesmas chaves.

from textwrap import dedent

try:
    import streamlit as st
except Exception:
    st = None  # evita falha de import em pipelines

# CSS local mínimo específico do painel (usa os mesmos tokens do tema)
_LOCAL_CSS = dedent("""
<style>
  /* Cartão padrão e tokens já vêm de ui/theme.py e .streamlit/config.toml */
  #EMAIL_PANEL{
    width: var(--email-w, 1306px);
    height: var(--email-h, 160px);
    margin: 0 auto;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--gap-2, 12px);
  }
  #EMAIL_PANEL .panel-card{
    background: transparent;
    border: var(--border, 1px solid rgba(234,242,247,.10));
    border-radius: var(--radius, 12px);
    box-shadow: var(--shadow, 0 4px 14px rgba(0,0,0,.18));
    padding: 10px var(--pad, 12px);
    height: calc(var(--email-h, 160px) - (2 * var(--pad, 12px)));
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: var(--gap-2, 12px);
    color: var(--text, #EAF2F7);
  }

  /* Abas com “orelhas” laranja permanentes (decorativas) */
  #EMAIL_PANEL .tabs{
    display: flex;
    gap: var(--gap-2, 12px);
    border-bottom: 1px solid var(--border-color, rgba(234,242,247,.10));
    padding: 0 var(--pad, 12px) 6px;
  }
  #EMAIL_PANEL .tab{
    position: relative;
    cursor: default;
    padding: 12px 12px 10px;
    border-bottom: 2px solid var(--accent, #FF8C32);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: var(--accent, #FF8C32);
    text-decoration: none;
  }
  #EMAIL_PANEL .tab::before{
    content:"";
    position:absolute;
    top:0; left:10px;
    width:18px; height:8px;
    background: var(--accent, #FF8C32);
    border-top-left-radius:6px;
    border-top-right-radius:6px;
  }

  /* Alertas (verde/erro) coerentes com o resto */
  #EMAIL_PANEL .alert{
    display:flex; align-items:center; gap:10px;
    border-radius:10px; padding:8px 10px;
    font-size:12px; line-height:1.2;
    border:1px solid var(--border-color, rgba(234,242,247,.10));
    background:rgba(255,255,255,.02);
  }
  #EMAIL_PANEL .alert-success{
    color:#22C55E;
    border-color: color-mix(in srgb, #22C55E 40%, transparent);
  }
  #EMAIL_PANEL .alert-error{
    color:#EF4444;
    border-color: color-mix(in srgb, #EF4444 40%, transparent);
  }

  /* Ajuste do grid do formulário: 3 colunas de inputs + 1 do botão */
  #EMAIL_PANEL .grid{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr auto;
    column-gap: var(--gap-3, 16px);
    row-gap: 8px;
    align-items: end;
    width: 100%;
    padding: 0 var(--pad, 12px);
  }
  #EMAIL_PANEL .field label{
    font-size: 12px; font-weight: 600; opacity:.9;
    display:block; margin-bottom:6px;
  }
  #EMAIL_PANEL .actions{
    display:flex; align-items:center; justify-content:flex-end;
  }
  /* Harmonização visual dos inputs nativos do Streamlit dentro do cartão */
  [data-baseweb="input"] input{
    background: rgba(255,255,255,.02) !important;
    color: var(--text, #EAF2F7) !important;
  }
</style>
""")

def _flash_messages():
    """
    Lê mensagens já definidas pela lógica existente (não alteramos nada).
    Convenções comuns suportadas (use a que já existe no seu app):
      - st.session_state['email_success'] / st.session_state['email_error']
      - st.session_state['flash_success'] / st.session_state['flash_error']
    """
    ss = getattr(st, "session_state", {})
    msg_ok = ss.get("email_success") or ss.get("flash_success")
    msg_er = ss.get("email_error") or ss.get("flash_error")
    return msg_ok, msg_er

def render_email_panel() -> None:
    """
    Desenha o painel de e-mail mantendo a lógica do envio/salvamento do seu app.
    - Campos: Remetente, Senha App, Enviar para
    - Botão: TESTAR/SALVAR (à direita)
    - Não executa envio: apenas UI. A lógica existente continua responsável.
    """
    if st is None:
        return  # ambiente sem Streamlit

    # Injeção de CSS local (visual apenas)
    st.markdown(_LOCAL_CSS, unsafe_allow_html=True)

    # Cartão 1306x160
    with st.container():
        # Estrutura externa fixa
        st.markdown('<div id="EMAIL_PANEL"><div class="panel-card">', unsafe_allow_html=True)

        # Abas (decorativas, não mudam navegação)
        st.markdown(
            '<nav class="tabs" aria-label="Painéis">'
            '<span class="tab">Email</span>'
            '<span class="tab">Moeda</span>'
            '<span class="tab">Entrada</span>'
            '<span class="tab">Saída</span>'
            '</nav>',
            unsafe_allow_html=True
        )

        # Alertas (se a lógica já tiver configurado mensagens no session_state)
        ok, er = _flash_messages()
        if ok:
            st.markdown(f'<div class="alert alert-success"><strong>Sucesso:</strong> {ok}</div>', unsafe_allow_html=True)
        if er:
            st.markdown(f'<div class="alert alert-error"><strong>Erro:</strong> {er}</div>', unsafe_allow_html=True)

        # Defaults vindos do session_state (mantém as mesmas chaves)
        defaults = getattr(st, "session_state", {})
        sender_default = defaults.get("sender", "")
        app_pwd_default = defaults.get("app_password", "")
        to_default = defaults.get("to_email", "")

        # Form visual. A ação/negócio continua no seu código já existente.
        with st.form("EMAIL_FORM_VISUAL", clear_on_submit=False):
            st.markdown('<div class="grid">', unsafe_allow_html=True)

            # 3 colunas de inputs + 1 do botão
            col1, col2, col3, col4 = st.columns([1, 1, 1, 0.35], gap="medium")
            with col1:
                st.markdown('<div class="field"><label>Remetente</label></div>', unsafe_allow_html=True)
                st.text_input(" ", key="sender", label_visibility="collapsed",
                              value=sender_default, placeholder="voce@dominio.com")
            with col2:
                st.markdown('<div class="field"><label>Senha App</label></div>', unsafe_allow_html=True)
                st.text_input("  ", key="app_password", label_visibility="collapsed",
                              value=app_pwd_default, type="password", placeholder="senha de app")
            with col3:
                st.markdown('<div class="field"><label>Enviar para</label></div>', unsafe_allow_html=True)
                st.text_input("   ", key="to_email", label_visibility="collapsed",
                              value=to_default, placeholder="destinatario@dominio.com")
            with col4:
                st.markdown('<div class="actions">', unsafe_allow_html=True)
                submitted = st.form_submit_button("TESTAR/SALVAR", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # fecha .grid

        # Não executamos nenhuma ação aqui: sua lógica atual continua observando o estado
        st.markdown('</div></div>', unsafe_allow_html=True)  # fecha panel-card e EMAIL_PANEL


# Execução direta opcional para testes manuais:
if __name__ == "__main__" and st is not None:
    st.set_page_config(layout="centered", page_title="Painel — Email")
    render_email_panel()
