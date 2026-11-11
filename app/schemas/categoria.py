from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema, UpdateSchema


class CategoriaCreate(CreateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Hortifruti"}]})

    nome: str = Field(min_length=2, max_length=60, description="Nome único da categoria.")


class CategoriaUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Frutas e Verduras"}]})

    nao_nulos = ("nome",)
    nome: Optional[str] = Field(default=None, min_length=2, max_length=60)


class CategoriaOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 1, "nome": "Grãos e Cereais"}]},
    )

    id: int
    nome: str
