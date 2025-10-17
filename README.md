# Autotrader — Fase 1


Automação Python para painéis **EMAIL → MOEDAS → ENTRADA → SAÍDA**.


## Como rodar local
```bash
python -m venv .venv && source .venv/bin/activate # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python - << 'PY'
from db import init_db; init_db()
print('DB ok')
PY
streamlit run aplicativo.py
