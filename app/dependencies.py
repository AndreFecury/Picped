"""Injeção de dependências: monta Connection -> Repositories -> Services para cada requisição."""
from typing import Iterator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.engine import Connection

from app.core.database import engine
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.lista_repository import ItemListaRepository, ListaRepository
from app.repositories.preco_repository import PrecoRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.supermercado_repository import SupermercadoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth_service import AuthService
from app.services.categoria_service import CategoriaService
from app.services.health_service import HealthService
from app.services.lista_service import ListaService
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


def get_lista_service(conn: Connection = Depends(get_conn)) -> ListaService:
    return ListaService(ListaRepository(conn), ItemListaRepository(conn), ProdutoRepository(conn))


def get_auth_service(conn: Connection = Depends(get_conn)) -> AuthService:
    return AuthService(UsuarioRepository(conn))


_bearer = HTTPBearer(auto_error=False, description="Token recebido em POST /auth/login.")


def get_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer),
    auth: AuthService = Depends(get_auth_service),
):
    """Usuário dono do token Bearer (401 se ausente, inválido ou expirado)."""
    return auth.usuario_do_token(credenciais.credentials if credenciais else None)


def get_usuario_opcional(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer),
    auth: AuthService = Depends(get_auth_service),
):
    """Igual ao anterior, mas permite chamada sem token (retorna None)."""
    return auth.usuario_do_token(credenciais.credentials) if credenciais else None
