from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema, UpdateSchema

_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioCreate(CreateSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"nome": "Diego Teste", "email": "diego@picped.dev", "senha": "senhaForte123"}]
        }
    )

    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=150, pattern=_EMAIL)
    senha: str = Field(min_length=8, max_length=72, description="Guardada apenas como hash (PBKDF2).")


class UsuarioUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Diego Souza"}]})

    nao_nulos = ("nome", "email", "senha")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = Field(default=None, max_length=150, pattern=_EMAIL)
    senha: Optional[str] = Field(default=None, min_length=8, max_length=72)


class UsuarioOut(BaseModel):
    """Nunca expõe a senha nem o hash."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"id": 1, "nome": "Ana Teste", "email": "ana@picped.dev", "criado_em": "2026-10-26T17:38:00"}
            ]
        },
    )

    id: int
    nome: str
    email: str
    criado_em: datetime
