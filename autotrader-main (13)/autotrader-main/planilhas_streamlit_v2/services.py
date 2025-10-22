# BLOCO 05 - INICIO (services.py)
from datetime import datetime
import pandas as pd
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from db import SessionLocal, engine, Base, init_db
from models import EmailSettings, Moeda, Entrada, Saida, AuditLog
from schemas import EmailCfg, MoedaIn, EntradaIn, SaidaIn
from config.tokens import DEFAULT_SYMBOLS, fmt_price, fmt_pct

Base.metadata.create_all(bind=engine)
init_db()

def _audit(session, tabela, registro_id, campo, antes, depois, user="operador"):
    session.add(AuditLog(tabela=tabela, registro_id=str(registro_id), campo=campo,
                         antes=str(antes), depois=str(depois), user=user))

# -------- EMAIL --------
def get_email_cfg():
    with SessionLocal() as s:
        row = s.scalar(select(EmailSettings).limit(1))
        return row

def save_email_cfg(data: EmailCfg):
    with SessionLocal() as s:
        row = s.scalar(select(EmailSettings).limit(1))
        if row is None:
            row = EmailSettings(principal=str(data.principal), envio=str(data.envio))
            s.add(row)
        else:
            _audit(s, "email_settings", row.id, "principal", row.principal, str(data.principal))
            _audit(s, "email_settings", row.id, "envio", row.envio, str(data.envio))
            row.principal = str(data.principal)
            row.envio = str(data.envio)
        s.commit()

# -------- MOEDAS --------
def bootstrap_moedas():
    with SessionLocal() as s:
        count = s.query(Moeda).count()
        if count == 0:
            for sym in DEFAULT_SYMBOLS:
                s.add(Moeda(simbolo=sym, nome="", ativo=True, obs=""))
            s.commit()

def list_moedas_df() -> pd.DataFrame:
    bootstrap_moedas()
    with SessionLocal() as s:
        rows = s.query(Moeda).order_by(Moeda.simbolo.asc()).all()
        return pd.DataFrame([{"Símbolo": r.simbolo, "Nome": r.nome or "", "Ativa?": r.ativo, "Observação": r.obs or ""} for r in rows])

def apply_moedas_df(df: pd.DataFrame):
    with SessionLocal() as s:
        for _, r in df.iterrows():
            m = s.query(Moeda).filter(Moeda.simbolo == str(r["Símbolo"]).upper()).one_or_none()
            if m:
                _audit(s, "moedas", m.id, "nome", m.nome, r["Nome"])
                _audit(s, "moedas", m.id, "ativo", m.ativo, r["Ativa?"])
                _audit(s, "moedas", m.id, "obs",   m.obs,   r["Observação"])
                m.nome = r["Nome"] or ""
                m.ativo = bool(r["Ativa?"])
                m.obs = r["Observação"] or ""
        s.commit()

# -------- ENTRADA --------
def list_entradas_df(modo: str) -> pd.DataFrame:
    with SessionLocal() as s:
        rows = s.query(Entrada).filter(Entrada.modo==modo).order_by(Entrada.simbolo.asc()).all()
        data = []
        for r in rows:
            data.append({
                "PARIDADE": r.simbolo, "SINAL": "NÃO ENTRAR" if r.ganho_pct==0 else "",
                "PREÇO": fmt_price(r.preco), "ALVO": fmt_price(r.alvo),
                "GANHO %": fmt_pct(r.ganho_pct), "DATA": r.data, "HORA": r.hora
            })
        return pd.DataFrame(data)

# -------- SAÍDA --------
def list_saidas_df() -> pd.DataFrame:
    with SessionLocal() as s:
        rows = s.query(Saida).order_by(Saida.id.desc()).all()
        data = []
        for r in rows:
            data.append({
                "PARIDADE": r.simbolo, "LADO": r.lado, "MODO": r.modo,
                "ENTRADA": fmt_price(r.entrada), "ALVO": fmt_price(r.alvo),
                "PREÇO ATUAL": fmt_price(r.preco_atual), "% de PNL": fmt_pct(r.pnl_pct),
                "DATA": r.data, "HORA": r.hora, "ALAV": r.alav, "EXCLUIR": False
            })
        return pd.DataFrame(data)
# BLOCO 05 - FIM
