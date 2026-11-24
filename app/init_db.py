"""Prepara o banco na primeira subida (ex.: Neon vazio no deploy do Render).

Se a tabela `usuario` ainda não existe, roda schema.sql + seed.sql + demo.sql.
Se já existe, não faz nada: nunca apaga dados de um banco em uso.
Uso: python -m app.init_db
"""
import sys
import time
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.database import engine

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
ARQUIVOS = ("schema.sql", "seed.sql", "demo.sql")


def preparar(tentativas: int = 10) -> str:
    for n in range(1, tentativas + 1):
        try:
            with engine.begin() as conn:
                existe = conn.execute(text("SELECT to_regclass('public.usuario')")).scalar()
                if existe:
                    return "banco já preparado; nada a fazer"
                for arq in ARQUIVOS:
                    conn.exec_driver_sql((SCRIPTS / arq).read_text(encoding="utf-8"))
                return "banco criado com schema, seed e dados de demonstração"
        except OperationalError as exc:  # banco serverless acordando
            if n == tentativas:
                raise
            print(f"init_db: banco indisponível ({exc.orig}); nova tentativa em 3 s", flush=True)
            time.sleep(3)
    return ""


if __name__ == "__main__":
    print("init_db:", preparar(), flush=True)
    sys.exit(0)
