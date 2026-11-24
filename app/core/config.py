"""Configurações lidas de variáveis de ambiente (.env em desenvolvimento)."""
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    pool_size: int
    pool_max_overflow: int
    pool_timeout: int
    pool_recycle: int
    connect_timeout: int
    secret_key: str
    token_horas: int
    cors_origens: list[str]
    database_url: str
    commit: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "picped"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "picped"),
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        pool_max_overflow=int(os.getenv("DB_POOL_MAX_OVERFLOW", "10")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
        connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        secret_key=os.getenv("SECRET_KEY", "picped-dev-troque-esta-chave"),
        token_horas=int(os.getenv("TOKEN_HORAS", "72")),
        cors_origens=[o.strip() for o in os.getenv("CORS_ORIGENS", "*").split(",") if o.strip()],
        # Em produção (Neon/Render) a conexão vem numa URL só; tem prioridade sobre DB_HOST/DB_NAME/...
        database_url=os.getenv("DATABASE_URL", ""),
        # Render preenche RENDER_GIT_COMMIT; o pipeline usa para saber qual versão está no ar
        commit=(os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_COMMIT") or "local")[:7],
    )
