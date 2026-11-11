from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaSchema, UpdateSchema

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioCreate(EntradaSchema):
    """Usado no POST e no PUT. A senha é recebida em texto e gravada só como hash."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"nome": "Diego Teste", "email": "diego@picped.dev", "senha": "Senha@123"}]
        }
    )
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=150, pattern=EMAIL)
    senha: str = Field(min_length=8, max_length=72, description="Mínimo de 8 caracteres")


class UsuarioUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Diego S. Teste"}]})
    nao_nulos = ("nome", "email", "senha")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = Field(default=None, max_length=150, pattern=EMAIL)
    senha: Optional[str] = Field(default=None, min_length=8, max_length=72)


class UsuarioOut(BaseModel):
    """Nunca devolve a senha nem o hash."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"id": 4, "nome": "Diego Teste", "email": "diego@picped.dev", "criado_em": "2026-11-11T10:00:00"}
            ]
        },
    )
    id: int
    nome: str
    email: str
    criado_em: datetime
