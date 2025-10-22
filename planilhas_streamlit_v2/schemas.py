# BLOCO 03 - INICIO (schemas.py)
from pydantic import BaseModel, EmailStr, constr, conint, confloat

class EmailCfg(BaseModel):
    principal: EmailStr
    envio: EmailStr
    # senha será guardada via st.secrets (nunca em DB)

class MoedaIn(BaseModel):
    simbolo: constr(strip_whitespace=True, to_upper=True, min_length=2, max_length=10)
    nome: constr(strip_whitespace=True) | None = None
    ativo: bool = True
    obs: str | None = None

class EntradaIn(BaseModel):
    simbolo: constr(to_upper=True)
    modo: constr(to_upper=True)       # SWING | POSICIONAL
    preco: confloat(ge=0) = 0
    alvo: confloat(ge=0) = 0
    ganho_pct: float = 0
    data: str = ""
    hora: str = ""

class SaidaIn(BaseModel):
    simbolo: constr(to_upper=True)
    lado: constr(to_upper=True)       # LONGAS | CURTO
    modo: constr(to_upper=True)       # SWING | POSICIONAL
    entrada: confloat(ge=0) = 0
    alvo: confloat(ge=0) = 0
    preco_atual: confloat(ge=0) = 0
    pnl_pct: float = 0
    data: str = ""
    hora: str = ""
    alav: conint(ge=1) = 1
# BLOCO 03 - FIM
