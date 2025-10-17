# Autotrader — Base Limpa (Fase 1)
Automação Python com 4 painéis (EMAIL → MOEDAS → ENTRADA → SAÍDA). Sem integrações externas.

## Rodar local
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python - <<'PY'
from db import init_db; init_db("autotrader.db")
print("DB ok")
PY
streamlit run aplicativo.py
```

## CI (required checks)
- `lint`, `typecheck`, `tests` — já configurados em `.github/workflows/ci.yml`.

Ative em **Settings → Branches → Branch protection** e selecione esses três checks.
