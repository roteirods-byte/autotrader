# BLOCO 02 - INICIO (models.py)
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from db import Base

class EmailSettings(Base):
    __tablename__ = "email_settings"
    id = Column(Integer, primary_key=True, index=True)
    principal = Column(String, nullable=False)
    envio = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Moeda(Base):
    __tablename__ = "moedas"
    id = Column(Integer, primary_key=True)
    simbolo = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    obs = Column(String, nullable=True)

class Entrada(Base):
    __tablename__ = "entradas"
    id = Column(Integer, primary_key=True)
    simbolo = Column(String, index=True)
    modo = Column(String)             # SWING | POSICIONAL
    preco = Column(Float, default=0.0)
    alvo  = Column(Float, default=0.0)
    ganho_pct = Column(Float, default=0.0)
    data = Column(String)             # dd/mm/aaaa
    hora = Column(String)             # HH:MM:SS

class Saida(Base):
    __tablename__ = "saidas"
    id = Column(Integer, primary_key=True)
    simbolo = Column(String, index=True)
    lado = Column(String)             # LONGAS | CURTO
    modo = Column(String)             # SWING | POSICIONAL
    entrada = Column(Float, default=0.0)
    alvo = Column(Float, default=0.0)
    preco_atual = Column(Float, default=0.0)
    pnl_pct = Column(Float, default=0.0)
    data = Column(String)
    hora = Column(String)
    alav = Column(Integer, default=1)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    tabela = Column(String)
    registro_id = Column(String)
    campo = Column(String)
    antes = Column(String)
    depois = Column(String)
    user = Column(String, default="operador")
    ts = Column(DateTime(timezone=True), server_default=func.now())
# BLOCO 02 - FIM
