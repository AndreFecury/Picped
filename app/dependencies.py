"""Injeção de dependências: monta Connection -> Repositories -> Services para cada requisição."""
from typing import Iterator

from fastapi import Depends
from sqlalchemy.engine import Connection

from app.core.database import engine
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.preco_repository import PrecoRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.supermercado_repository import SupermercadoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.categoria_service import CategoriaService
from app.services.health_service import HealthService
from app.services.preco_service import PrecoService
from app.services.produto_service import ProdutoService
from app.services.supermercado_service import SupermercadoService
from app.services.usuario_service import UsuarioService


def get_conn() -> Iterator[Connection]:
    """Pega uma conexão do pool e a devolve ao final da requisição (rollback se algo falhou)."""
    with engine.connect() as conn:
        yield conn


def get_categoria_service(conn: Connection = Depends(get_conn)) -> CategoriaService:
    return CategoriaService(CategoriaRepository(conn))


def get_produto_service(conn: Connection = Depends(get_conn)) -> ProdutoService:
    return ProdutoService(ProdutoRepository(conn), CategoriaRepository(conn))


def get_supermercado_service(conn: Connection = Depends(get_conn)) -> SupermercadoService:
    return SupermercadoService(SupermercadoRepository(conn))


def get_preco_service(conn: Connection = Depends(get_conn)) -> PrecoService:
    return PrecoService(
        PrecoRepository(conn),
        ProdutoRepository(conn),
        SupermercadoRepository(conn),
        UsuarioRepository(conn),
    )


def get_usuario_service(conn: Connection = Depends(get_conn)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(conn))


def get_health_service(conn: Connection = Depends(get_conn)) -> HealthService:
    return HealthService(HealthRepository(conn))
