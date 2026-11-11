from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaSchema, UpdateSchema

_EXEMPLO = {
    "produto_id": 1,
    "supermercado_id": 2,
    "usuario_id": 1,
    "valor": 29.90,
    "coletado_em": "2026-11-11T09:30:00",
    "distancia_metros": 20,
}


class PrecoCreate(EntradaSchema):
    """Usado no POST e no PUT (substituição completa)."""

    model_config = ConfigDict(json_schema_extra={"examples": [_EXEMPLO]})
    produto_id: int = Field(gt=0, strict=True)
    supermercado_id: int = Field(gt=0, strict=True)
    usuario_id: int = Field(gt=0, strict=True)
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2, description="Preço em R$")
    coletado_em: Optional[datetime] = Field(default=None, description="Se omitido, usa a data/hora atual")
    distancia_metros: Optional[int] = Field(
        default=None, ge=0, strict=True, description="Distância do usuário ao mercado (GPS)"
    )


class PrecoUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"valor": 27.49}]})
    nao_nulos = ("valor",)
    valor: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class PrecoOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [{"id": 31, **_EXEMPLO}]}
    )
    id: int
    produto_id: int
    supermercado_id: int
    usuario_id: int
    valor: float
    coletado_em: datetime
    distancia_metros: Optional[int]


class OfertaOut(BaseModel):
    supermercado_id: int
    supermercado_nome: str
    valor: float
    coletado_em: datetime


class ComparacaoOut(BaseModel):
    produto_id: int
    produto_nome: str
    menor_preco: Optional[OfertaOut]
    maior_preco: Optional[OfertaOut]
    economia: float
    economia_percentual: float
    ofertas: list[OfertaOut]
