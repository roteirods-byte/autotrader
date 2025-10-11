# services/persist.py
import json, os

BASE = os.getenv("DB_PATH", "/data")
F_MOEDAS = os.path.join(BASE, "moedas.json")

DEFAULT_MOEDAS = [
    {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
    {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1},
]

def load_moedas():
    try:
        with open(F_MOEDAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_MOEDAS.copy()

def save_moedas(rows):
    os.makedirs(BASE, exist_ok=True)
    with open(F_MOEDAS, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
