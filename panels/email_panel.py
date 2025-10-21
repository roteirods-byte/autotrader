
# panels/email_panel.py  — Streamlit puro (sem HTML/CSS extra)
# Mantém sua lógica. Só organiza o layout com colunas nativas.

import streamlit as st

def _flash_messages():
    ss = st.session_state
    ok = ss.get("email_success") or ss.get("flash_success")
    er = ss.get("email_error") or ss.get("flash_error")
    return ok, er

def render_email_panel() -> None:
    # Mensagens (se sua lógica setar no session_state)
    ok, er = _flash_messages()
    if ok:
        st.success(ok, icon="✅")
    if er:
        st.error(er, icon="⚠️")

    # Formulário nativo: 3 campos + 1 coluna só para o botão
    with st.form("EMAIL_FORM", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns([3, 3, 3, 2], gap="medium")

        with c1:
            st.text_input(
                "Remetente",
                key="sender",
                value=st.session_state.get("sender", st.session_state.get("sender_email", "")),
                placeholder="voce@dominio.com",
            )

        with c2:
            st.text_input(
                "Senha App",
                key="app_password",
                value=st.session_state.get("app_password", st.session_state.get("email_app_password", "")),
                type="password",
                placeholder="senha de app",
            )

        with c3:
            st.text_input(
                "Enviar para",
                key="to_email",
                value=st.session_state.get("to_email", st.session_state.get("email_to", "")),
                placeholder="destinatario@dominio.com",
            )

        with c4:
            # Pequeno espaçamento para alinhar verticalmente o botão
            st.write("")
            st.write("")
            submitted = st.form_submit_button("TESTAR/SALVAR")

        # Sinal para sua lógica (se usar)
        st.session_state["email_submit"] = submitted

    # Espelhos de chaves (se sua lógica usa estes nomes)
    st.session_state["sender_email"] = st.session_state.get("sender", "")
    st.session_state["email_app_password"] = st.session_state.get("app_password", "")
    st.session_state["email_to"] = st.session_state.get("to_email", "")
