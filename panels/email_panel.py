# panels/email_panel.py
import re
import streamlit as st

# CSS global (abas laranja, inputs/botão 250px, gap 50px, painel 1306x160)
def _inject_css():
    st.markdown(
        """
        <style>
          .stTabs [data-baseweb="tab"] p { color:#ff7b1b !important; font-weight:700; }
          .stTabs [aria-selected="true"] { border-color:#ff7b1b !important; }
          .email-panel { width:1306px; height:160px; background:#08202B; 
                         border:2px solid #ffffff; border-radius:8px; padding:16px; }
          .email-row { display:flex; gap:50px; align-items:center; }
          .email-row .fxw input, .email-row .fxw textarea { width:250px !important; }
          .email-row .btn250 button { width:250px !important; height:40px; 
                                      background:#ff7b1b !important; color:#0b2533 !important; font-weight:700; }
          .ok-badge { background:#0d5f3f; color:#e7edf3; padding:8px 12px; border-radius:6px; }
          .err-badge{ background:#7a1b1b; color:#e7edf3; padding:8px 12px; border-radius:6px; }
          label, .st-emotion-cache-ue6h4q p { color:#e7edf3 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _is_email(v:str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v or ""))

def _smtp_send(gmail_user:str, app_password:str, to_addr:str) -> tuple[bool,str]:
    # tenta usar serviço do projeto; se não houver, usa SMTP direto
    try:
        from ops.email_svc import send_test_email  # já instalado por você
        ok, msg = send_test_email(gmail_user, app_password, to_addr)
        return bool(ok), str(msg)
    except Exception:
        import smtplib
        from email.mime.text import MIMEText
        try:
            msg = MIMEText("Teste de e-mail do AUTOTRADER (Painel EMAIL).")
            msg["Subject"] = "[AUTOTRADER] Teste de e-mail"
            msg["From"] = gmail_user
            msg["To"] = to_addr
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(gmail_user, app_password)
                smtp.sendmail(gmail_user, [to_addr], msg.as_string())
            return True, "Enviado"
        except Exception as e:
            return False, f"Erro SMTP: {e}"

def _load_from_db():
    try:
        from ops.db import get_session
        from ops.models import EmailSetting
        with get_session() as s:
            row = s.query(EmailSetting).order_by(EmailSetting.id.desc()).first()
            if row:
                return {"mail_user": row.mail_user or "", "mail_from": row.mail_from or "", "mail_to": row.mail_to or ""}
    except Exception:
        pass
    return {"mail_user": "", "mail_from": "", "mail_to": ""}

def _save_to_db(mail_from:str, mail_to:str, mail_user:str):
    try:
        from ops.db import get_session
        from ops.models import EmailSetting
        with get_session() as s:
            obj = EmailSetting(mail_from=mail_from, mail_to=mail_to, mail_user=mail_user)
            s.add(obj); s.commit()
        return True
    except Exception:
        return False

def render():
    _inject_css()
    st.markdown('<div class="email-panel">', unsafe_allow_html=True)

    # Título padrão do projeto
    st.markdown("### EMAIL")

    # carregar valores já salvos
    if "email_form" not in st.session_state:
        st.session_state.email_form = _load_from_db()

    col = st.container()
    with col:
        st.markdown('<div class="email-row">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1,1,1,1], vertical_alignment="center")
        with c1:
            mail_user = st.text_input("E-mail (remetente)", 
                                      value=st.session_state.email_form.get("mail_user",""), 
                                      key="mail_user", help="Seu Gmail que envia")
        with c2:
            app_pwd = st.text_input("App Password (Gmail)", type="password", key="mail_pwd", help="Senha de App de 16 dígitos")
        with c3:
            mail_to = st.text_input("Enviar para", 
                                    value=st.session_state.email_form.get("mail_to",""), 
                                    key="mail_to", help="Destino dos alertas")
        with c4:
            st.markdown('<div class="btn250">', unsafe_allow_html=True)
            acao = st.button("TESTAR/SALVAR", use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Validação simples
        if acao:
            if not _is_email(mail_user) or not _is_email(mail_to):
                st.markdown('<div class="err-badge">E-mails inválidos.</div>', unsafe_allow_html=True)
            elif len(app_pwd.strip()) < 16:
                st.markdown('<div class="err-badge">App Password inválida (16 caracteres).</div>', unsafe_allow_html=True)
            else:
                ok_send, msg = _smtp_send(mail_user, app_pwd, mail_to)
                ok_db = _save_to_db(mail_user, mail_to, mail_user)
                if ok_send:
                    st.markdown('<div class="ok-badge">Configuração salva e e-mail de teste enviado ✅</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="err-badge">Falha no envio: {msg}</div>', unsafe_allow_html=True)
                if not ok_db:
                    st.caption("Aviso: não foi possível salvar no banco (seguimos só com envio).")

    st.markdown('</div>', unsafe_allow_html=True)
