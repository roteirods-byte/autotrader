# ops/email_svc.py
from __future__ import annotations
import smtplib, ssl
from email.mime.text import MIMEText

def send_test_email(mail_user: str, app_password: str, mail_to: str) -> tuple[bool, str]:
    try:
        msg = MIMEText("Teste de e-mail do AUTOTRADER: configuração OK.")
        msg["Subject"] = "[AUTOTRADER] Teste de e-mail"
        msg["From"] = mail_user
        msg["To"] = mail_to

        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(mail_user, app_password)
            server.sendmail(mail_user, [mail_to], msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)
