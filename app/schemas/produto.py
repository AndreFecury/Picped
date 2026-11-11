from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaSchema, UpdateSchema

Unidade = Literal["un", "kg", "g", "l", "ml"]

_EXEMPLO = {
    "nome": "Macarrão Espaguete 500g",
    "marca": "Renata",
    "unidade_medida": "un",
    "codigo_barras": "7896022200103",
    "categoria_id": 7,
}


class ProdutoCreate(EntradaSchema):
    """Usado no POST e no PUT (substituição completa)."""

    model_config = ConfigDict(json_schema_extra={"examples": [_EXEMPLO]})
    nome: str = Field(min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Unidade = Field(description="un, kg, g, l ou ml")
    codigo_barras: Optional[str] = Field(
        default=None, pattern=r"^[0-9]{8,14}$", description="EAN-8/13/14 (só dígitos)"
    )
    categoria_id: int = Field(gt=0, strict=True)


class ProdutoUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"marca": "Barilla"}]})
    nao_nulos = ("nome", "unidade_medida", "categoria_id")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Optional[Unidade] = None
    codigo_barras: Optional[str] = Field(default=None, pattern=r"^[0-9]{8,14}$")
    categoria_id: Optional[int] = Field(default=None, gt=0, strict=True)


class ProdutoOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [{"id": 13, **_EXEMPLO}]}
    )
    id: int
    nome: str
    marca: Optional[str]
    unidade_medida: str
    codigo_barras: Optional[str]
    categoria_id: int
