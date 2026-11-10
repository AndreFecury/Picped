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
    )
