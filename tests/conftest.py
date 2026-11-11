"""
Fixtures dos testes. Os testes rodam contra um PostgreSQL de verdade (o mesmo do projeto),
num banco SEPARADO: TEST_DB_NAME (padrão: picped_test), criado automaticamente se não existir.
Antes de CADA teste o banco é recriado com scripts/schema.sql + scripts/seed.sql
(um teste nunca interfere no outro).
"""
import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg import sql

load_dotenv()
_BANCO_TESTE = os.getenv("TEST_DB_NAME", "picped_test")
if _BANCO_TESTE == os.getenv("DB_NAME", "picped"):
    raise RuntimeError("TEST_DB_NAME não pode ser o banco principal: os testes apagam as tabelas.")
# precisa vir ANTES de importar a app: o engine é criado na importação
os.environ["DB_NAME"] = _BANCO_TESTE

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SQL_RESET = (SCRIPTS / "schema.sql").read_text(encoding="utf-8") + "\n" + (
    SCRIPTS / "seed.sql"
).read_text(encoding="utf-8")


def _conectar(dbname: str) -> psycopg.Connection:
    s = get_settings()
    return psycopg.connect(
        host=s.db_host,
        port=s.db_port,
        dbname=dbname,
        user=s.db_user,
        password=s.db_password,
        autocommit=True,
        connect_timeout=s.connect_timeout,
    )


def _garantir_banco_de_teste(nome: str) -> None:
    """Cria o banco de teste se ainda não existir (conectando no banco de manutenção 'postgres')."""
    with _conectar("postgres") as conn:
        existe = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome,)).fetchone()
        if not existe:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nome)))


@pytest.fixture(scope="session")
def conexao_admin():
    nome = get_settings().db_name
    try:
        _garantir_banco_de_teste(nome)
        conn = _conectar(nome)
    except psycopg.OperationalError as exc:
        pytest.exit(f"PostgreSQL de teste indisponível ({exc}). Veja a seção 'Testes' do README.")
    with conn:
        conn.execute("SET client_min_messages TO WARNING")  # esconde os NOTICE do DROP IF EXISTS
        yield conn


@pytest.fixture(autouse=True)
def banco_limpo(conexao_admin):
    """Recria schema + seed antes de cada teste (estado conhecido e isolado)."""
    conexao_admin.execute(SQL_RESET)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # TestClient usa HTTPX por baixo
        yield c


def assert_erro(resp, status: int, codigo: str | None = None) -> dict:
    """Valida o formato padrão de erro: {"erro": {"codigo": str, "mensagem": str, ...}}."""
    assert resp.status_code == status, resp.text
    corpo = resp.json()
    assert set(corpo) == {"erro"}
    assert isinstance(corpo["erro"]["codigo"], str)
    assert isinstance(corpo["erro"]["mensagem"], str) and corpo["erro"]["mensagem"]
    if codigo:
        assert corpo["erro"]["codigo"] == codigo
    return corpo["erro"]


def campos_com_erro(resp) -> set[str]:
    return {d["campo"] for d in resp.json()["erro"].get("detalhes", [])}
