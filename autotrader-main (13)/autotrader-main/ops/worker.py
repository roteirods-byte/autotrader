from __future__ import annotations
from datetime import datetime
import os
import pytz

TZ = os.getenv("TZ", "America/Sao_Paulo")


def main() -> None:
    tz = pytz.timezone(TZ)
    print(f"worker tick @ {datetime.now(tz).isoformat()}")
    # futuro: cálculos, atualização de PL%, geração de registros de EMAIL etc.


if __name__ == "__main__":
    main()
