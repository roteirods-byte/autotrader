# ops/email_templates.py
from datetime import datetime
from typing import Tuple

def teste(remetente:str, destino:str) -> Tuple[str,str]:
    assunto = "[AUTOTRADER] Teste de e-mail"
    corpo = f"Teste de envio OK.\nRemetente: {remetente}\nDestino: {destino}\nData: {datetime.now():%Y-%m-%d %H:%M:%S}"
    return assunto, corpo

def entrada(symbol:str, side:str, preco:float, alvo:float, pnl_pct:float) -> Tuple[str,str]:
    a = f"[AUTOTRADER] ENTRADA {symbol} {side}"
    b = f"{symbol} {side}\nPreço: {preco:.3f}\nAlvo: {alvo:.3f}\nPnL%: {pnl_pct:.2f}\nData: {datetime.now():%Y-%m-%d %H:%M:%S}"
    return a, b

def saida(symbol:str, preco:float, alvo:float, pnl_pct:float) -> Tuple[str,str]:
    a = f"[AUTOTRADER] SAÍDA {symbol}"
    b = f"{symbol}\nPreço: {preco:.3f}\nAlvo: {alvo:.3f}\nPnL%: {pnl_pct:.2f}\nData: {datetime.now():%Y-%m-%d %H:%M:%S}"
    return a, b
