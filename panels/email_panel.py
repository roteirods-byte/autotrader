import os, re, streamlit as st
from email.mime.text import MIMEText

def _is_email(v:str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v or ""))

def _smtp_send(gmail_user:str, app_password:str, to_addr:str) -> tuple[bool,str]:
    # tenta serviço; se não houver, usa SMTP direto
    try:
        from ops.email_svc import send_test_email
        ok, msg = send_test_email(gmail_user, app_password, to_addr)
        return bool(ok), str(msg)
    except Exception:
        import smtplib
        try:
            msg = MIMEText("Teste de e-mail do AUTOTRADER (Painel EMAIL).")
            msg["Subject"] = "[AUTOTRADER] Teste de e-mail"
            msg["From"] = gmail_user
            msg["To"] = to_addr
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
                s.starttls(); s.login(gmail_user, app_password); s.sendmail(gmail_user, [to_addr], msg.as_string())
            return True, "Enviado"
        except Exception as e:
            return False, f"{e}"

def _load_defaults():
    # fallback: ENV VARS se DB não existir
    return {
        "mail_user": os.getenv("MAIL_USER", ""),
        "mail_to": os.getenv("MAIL_TO", ""),
    }

def render():
    # CSS mínimo para largura dos inputs/botão
    st.markdown("""
    <style>
      div[data-baseweb="input"] input {max-width:250px; width:250px;}
      div.row-widget.stButton button {width:250px; height:40px;}
      .hint {opacity:.7; font-size:0.85rem;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### EMAIL")

    defaults = _load_defaults()
    c1, c2, c3, c4 = st.columns([1,1,1,1], vertical_alignment="center")

    with c1:
        mail_user = st.text_input("E-mail (remetente)", value=defaults["mail_user"], help="Seu Gmail que envia")
    with c2:
        app_pwd = st.text_input("App Password (Gmail)", type="password", help="Senha de App de 16 dígitos")
    with c3:
        mail_to = st.text_input("Enviar para", value=defaults["mail_to"], help="Destino dos alertas")
    with c4:
        acao = st.button("TESTAR/SALVAR")

    if acao:
        if not _is_email(mail_user) or not _is_email(mail_to):
            st.error("E-mails inválidos.")
            return
        if len(app_pwd.strip()) < 16:
            st.error("App Password inválida (16 caracteres).")
            return
        ok, msg = _smtp_send(mail_user, app_pwd, mail_to)
        if ok:
            st.success("Configuração salva e e-mail de teste enviado ✅")
            # grava simples no DB (se existir)
            try:
                from ops.db import get_session
                from ops.models import EmailSetting
                with get_session() as s:
                    s.add(EmailSetting(mail_from=mail_user, mail_to=mail_to, mail_user=mail_user)); s.commit()
            except Exception:
                pass
        else:
            st.error(f"Falha no envio: {msg}")
