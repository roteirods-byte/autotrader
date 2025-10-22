# BLOCO 04 - INICIO (tokens.py)
PREC_DECIMALS = 3
PCT_DECIMALS  = 2

DEFAULT_SYMBOLS = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK",
    "LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB",
    "SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

def fmt_price(x: float) -> str:
    return f"{float(x):.{PREC_DECIMALS}f}"

def fmt_pct(x: float) -> str:
    return f"{float(x):.{PCT_DECIMALS}f}"
# BLOCO 04 - FIM
