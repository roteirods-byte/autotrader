# services/persist.py
from pathlib import Path
import json

# Cria a pasta "data" DENTRO do projeto (gravável na Render)
BASE = Path(__file__).resolve().parents[1] / "data"
BASE.mkdir(parents=True, exist_ok=True)

MOEDAS_PATH = BASE / "moedas.json"

def save_moedas(rows: list[dict]) -> None:
    """Salva a lista de moedas (linhas da tabela) como JSON."""
    MOEDAS_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2))

def load_moedas() -> list[dict]:
    """Lê as moedas do arquivo; se não existir, devolve um default."""
    if MOEDAS_PATH.exists():
        return json.loads(MOEDAS_PATH.read_text())
    return [
        {"Par": "BTC/USDT", "Filtro": "Top10", "Peso": 1},
        {"Par": "ETH/USDT", "Filtro": "Top10", "Peso": 1},
    ]
