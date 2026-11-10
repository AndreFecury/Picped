from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UpdateSchema

Unidade = Literal["un", "kg", "g", "l", "ml"]


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Unidade
    codigo_barras: Optional[str] = Field(default=None, pattern=r"^[0-9]{8,14}$")
    categoria_id: int = Field(gt=0)


class ProdutoUpdate(UpdateSchema):
    nao_nulos = ("nome", "unidade_medida", "categoria_id")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Optional[Unidade] = None
    codigo_barras: Optional[str] = Field(default=None, pattern=r"^[0-9]{8,14}$")
    categoria_id: Optional[int] = Field(default=None, gt=0)


class ProdutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    marca: Optional[str]
    unidade_medida: str
    codigo_barras: Optional[str]
    categoria_id: int
