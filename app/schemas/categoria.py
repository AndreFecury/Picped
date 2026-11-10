from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UpdateSchema


class CategoriaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=60)


class CategoriaUpdate(UpdateSchema):
    nao_nulos = ("nome",)
    nome: Optional[str] = Field(default=None, min_length=2, max_length=60)


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
