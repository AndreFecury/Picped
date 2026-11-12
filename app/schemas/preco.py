from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema, UpdateSchema


class PrecoCreate(CreateSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "produto_id": 1,
                    "supermercado_id": 1,
                    "usuario_id": 1,
                    "valor": "27.90",
                    "coletado_em": "2026-11-11T10:30:00",
                    "distancia_metros": 15,
                }
            ]
        }
    )

    produto_id: int = Field(gt=0)
    supermercado_id: int = Field(gt=0)
    usuario_id: int = Field(gt=0)
    # strict=False só nestes campos: JSON não tem tipo Decimal/datetime, então aceitam número/texto
    valor: Decimal = Field(
        gt=0, max_digits=10, decimal_places=2, strict=False, description="Preço em R$ (até 2 casas)."
    )
    coletado_em: Optional[datetime] = Field(
        default=None, strict=False, description="ISO 8601. Se omitido, o banco usa a data/hora atual."
    )
    distancia_metros: Optional[int] = Field(
        default=None, ge=0, description="Distância do usuário até o mercado (GPS); não pode passar do raio."
    )


class PrecoUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"valor": "26.49"}]})

    nao_nulos = ("valor",)
    valor: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2, strict=False)


class PrecoOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "produto_id": 1,
                    "supermercado_id": 1,
                    "usuario_id": 1,
                    "valor": 27.9,
                    "coletado_em": "2026-10-05T10:15:00",
                    "distancia_metros": 12,
                }
            ]
        },
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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "produto_id": 1,
                    "produto_nome": "Arroz Branco Tipo 1 5kg",
                    "menor_preco": {
                        "supermercado_id": 1,
                        "supermercado_nome": "Atacadão",
                        "valor": 28.5,
                        "coletado_em": "2026-10-19T18:40:00",
                    },
                    "maior_preco": {
                        "supermercado_id": 3,
                        "supermercado_nome": "DB",
                        "valor": 32.9,
                        "coletado_em": "2026-10-14T17:05:00",
                    },
                    "economia": 4.4,
                    "economia_percentual": 13.37,
                    "ofertas": [],
                }
            ]
        }
    )

    produto_id: int
    produto_nome: str
    menor_preco: Optional[OfertaOut]
    maior_preco: Optional[OfertaOut]
    economia: float
    economia_percentual: float
    ofertas: list[OfertaOut]


class PontoHistoricoOut(BaseModel):
    valor: float
    coletado_em: datetime
    supermercado_id: int
    supermercado_nome: str


class HistoricoOut(BaseModel):
    produto_id: int
    produto_nome: str
    registros: int
    minimo: Optional[float]
    maximo: Optional[float]
    media: Optional[float]
    variacao_percentual: Optional[float] = Field(description="Do primeiro para o último registro.")
    pontos: list[PontoHistoricoOut]
