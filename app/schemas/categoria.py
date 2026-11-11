from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaSchema, UpdateSchema


class CategoriaCreate(EntradaSchema):
    """Usado no POST e no PUT (substituição completa)."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Padaria"}]})
    nome: str = Field(min_length=2, max_length=60, description="Nome único da categoria")


class CategoriaUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Padaria e Confeitaria"}]})
    nao_nulos = ("nome",)
    nome: Optional[str] = Field(default=None, min_length=2, max_length=60)


class CategoriaOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [{"id": 8, "nome": "Padaria"}]}
    )
    id: int
    nome: str
