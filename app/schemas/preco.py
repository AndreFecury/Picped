from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UpdateSchema


class PrecoCreate(BaseModel):
    produto_id: int = Field(gt=0)
    supermercado_id: int = Field(gt=0)
    usuario_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    coletado_em: Optional[datetime] = None
    distancia_metros: Optional[int] = Field(default=None, ge=0)


class PrecoUpdate(UpdateSchema):
    nao_nulos = ("valor",)
    valor: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class PrecoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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
