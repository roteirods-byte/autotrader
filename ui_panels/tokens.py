# BLOCO 01 - INICIO (tokens.py)
# Design tokens, formatos e constantes compartilhadas.

APP_TITLE = "PAINÉIS DA AUTOMAÇÃO"
BG_COLOR = "#0D1B24"          # azul-escuro de fundo
TITLE_COLOR = "#FF8C00"       # "abóbora"
BORDER_COLOR = "#FFFFFF"      # borda branca
LONG_COLOR = "#00C853"        # verde
SHORT_COLOR = "#FF5252"       # vermelho

# Larguras fixas e dimensões
EMAIL_W = 1306
EMAIL_H = 160

# Formatação numérica
PREC_DECIMALS = 3   # preços com 3 casas
PCT_DECIMALS  = 2   # percentuais com 2 casas

# Lista padrão (39 moedas) — ordem alfabética
DEFAULT_SYMBOLS = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC",
    "DOGE","DOT","ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK",
    "LTC","NEAR","OP","PEPE","POL","RATS","RENDER","RUNE","SEI","SHIB",
    "SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]

# Chaves de sessão
SS_EMAIL = "ss_email_cfg"
SS_COINS = "ss_coins"
SS_ENTRADA = "ss_entrada"
SS_SAIDA = "ss_saida"

def fmt_price(x):
    try:
        return f"{float(x):.{PREC_DECIMALS}f}"
    except Exception:
        return x

def fmt_pct(x):
    try:
        return f"{float(x):.{PCT_DECIMALS}f}"
    except Exception:
        return x

def today_date_time():
    import datetime as _dt
    now = _dt.datetime.now()
    return now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S")
# BLOCO 01 - FIM
