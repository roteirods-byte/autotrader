from __future__ import annotations
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .db import Base

class Coin(Base):
    __tablename__ = "coins"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False)
    note = Column(String(200), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True, nullable=False)
    side = Column(String(5), nullable=False)  # LONG | SHORT
    mode = Column(String(12), nullable=False) # Swing | Posicional
    entry_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    pnl_pct = Column(Float, default=0.0)
    status = Column(String(12), default="ABERTA") # ABERTA | FECHADA
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_date = Column(String(10))  # YYYY-MM-DD
    created_time = Column(String(8))   # HH:MM:SS

class Exit(Base):
    __tablename__ = "exits"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True, nullable=False)
    side = Column(String(5), nullable=False)
    mode = Column(String(12), nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    pnl_pct = Column(Float, default=0.0)
    status = Column(String(12), default="FECHADA") # FECHADA | ALERTA
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_date = Column(String(10))
    created_time = Column(String(8))

class EmailSetting(Base):
    __tablename__ = "email_settings"
    id = Column(Integer, primary_key=True)
    mail_from = Column(String(120))
    mail_to = Column(String(120))
    mail_user = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmailLog(Base):
    __tablename__ = "email_log"
    id = Column(Integer, primary_key=True)
    subject = Column(String(200))
    body = Column(Text)
    status = Column(String(20))  # SENT | ERROR
    created_at = Column(DateTime(timezone=True), server_default=func.now())
