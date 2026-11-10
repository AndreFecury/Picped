"""Engine do SQLAlchemy com pool de conexões (criado uma vez, reutilizado em todas as requisições)."""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from app.core.config import get_settings

_settings = get_settings()

engine = create_engine(
    # URL.create escapa corretamente senhas com caracteres especiais
    URL.create(
        "postgresql+psycopg",
        username=_settings.db_user,
        password=_settings.db_password,
        host=_settings.db_host,
        port=_settings.db_port,
        database=_settings.db_name,
    ),
    pool_size=_settings.pool_size,
    max_overflow=_settings.pool_max_overflow,
    pool_timeout=_settings.pool_timeout,  # espera máxima (s) por uma conexão livre
    pool_recycle=_settings.pool_recycle,  # renova conexões antigas (s)
    pool_pre_ping=True,                   # testa a conexão antes de usar (evita conexões mortas)
    connect_args={
        "connect_timeout": _settings.connect_timeout,  # falha rápido (503) se o banco cair
        "application_name": "picped-api",              # identifica a API no pg_stat_activity
    },
)
