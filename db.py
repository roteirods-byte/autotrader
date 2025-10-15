# db.py
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, BigInteger, Float, Integer, Boolean, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DATABASE_URL = os.getenv("DATABASE_URL", "")

class Base(DeclarativeBase):
    pass

class Moeda(Base):
    __tablename__ = "moedas"
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    leverage: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[int] = mapped_column(BigInteger, default=lambda: int(datetime.utcnow().timestamp()))

class Estrategia(Base):
    __tablename__ = "estrategias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10), index=True)  # 10m, 4H, 1D
    params: Mapped[str] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class Sinal(Base):
    __tablename__ = "sinais"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[int] = mapped_column(BigInteger, index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10), index=True)
    side: Mapped[str] = mapped_column(String(5))                    # LONG/SHORT/FLAT
    score: Mapped[float] = mapped_column(Float, default=0.0)

class Ordem(Base):
    __tablename__ = "ordens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[int] = mapped_column(BigInteger, index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(5))
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))                 # NEW/FILLED/CANCELED/ERROR
    error: Mapped[Optional[str]] = mapped_column(Text, default=None)

class Posicao(Base):
    __tablename__ = "posicoes"
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    qty: Mapped[float] = mapped_column(Float, default=0.0)
    avg_price: Mapped[float] = mapped_column(Float, default=0.0)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    ts: Mapped[int] = mapped_column(BigInteger, default=lambda: int(datetime.utcnow().timestamp()))

class Auditoria(Base):
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[int] = mapped_column(BigInteger, index=True)
    etapa: Mapped[str] = mapped_column(String(40))
    detalhe_json: Mapped[str] = mapped_column(Text)

class Health(Base):
    __tablename__ = "health"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column(String(30), index=True)    # 'worker'
    value: Mapped[str] = mapped_column(String(40))                  # 'alive'
    ts: Mapped[int] = mapped_column(BigInteger, index=True)

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não definido no ambiente.")
    return create_engine(DATABASE_URL, pool_pre_ping=True)

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def heartbeat(service: str, value: str = "alive"):
    engine = get_engine()
    with Session(engine) as s:
        s.execute(text("INSERT INTO health(service,value,ts) VALUES(:a,:b,EXTRACT(EPOCH FROM NOW()))"),
                  {"a": service, "b": value})
        s.commit()
