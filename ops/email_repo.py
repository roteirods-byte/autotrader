# ops/email_repo.py
from __future__ import annotations
import os
from typing import Optional, Dict
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///autotrader.db")

_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
Base = declarative_base()

class EmailSetting(Base):
    __tablename__ = "email_settings"
    id = Column(Integer, primary_key=True)
    mail_from = Column(String(120))
    mail_to = Column(String(120))
    mail_user = Column(String(120))

def init_db():
    Base.metadata.create_all(_engine)

def load_email_settings() -> Optional[Dict[str, str]]:
    with _Session() as s:
        row = s.query(EmailSetting).order_by(EmailSetting.id.desc()).first()
        if not row:
            return None
        return {"mail_from": row.mail_from or "", "mail_to": row.mail_to or "", "mail_user": row.mail_user or ""}

def save_email_settings(mail_from: str, mail_to: str, mail_user: str) -> None:
    with _Session() as s:
        row = s.query(EmailSetting).order_by(EmailSetting.id.desc()).first()
        if not row:
            row = EmailSetting(mail_from=mail_from, mail_to=mail_to, mail_user=mail_user)
            s.add(row)
        else:
            row.mail_from = mail_from
            row.mail_to = mail_to
            row.mail_user = mail_user
        s.commit()
