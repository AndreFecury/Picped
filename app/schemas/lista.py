from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema, UpdateSchema


class ListaCreate(CreateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Compra do mês"}]})

    nome: str = Field(min_length=2, max_length=100)


class ListaUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"nome": "Compra da semana"}]})

    nao_nulos = ("nome",)
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)


class ListaResumoOut(BaseModel):
    id: int
    nome: str
    criada_em: datetime
    total_itens: int


class ItemCreate(CreateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"produto_id": 1, "quantidade": 2}]})

    produto_id: int = Field(gt=0)
    quantidade: Decimal = Field(default=Decimal("1"), gt=0, le=9999, decimal_places=3, strict=False)


class ItemUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"quantidade": 3, "comprado": True}]})

    nao_nulos = ("quantidade", "comprado")
    quantidade: Optional[Decimal] = Field(default=None, gt=0, le=9999, decimal_places=3, strict=False)
    comprado: Optional[bool] = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lista_id: int
    produto_id: int
    quantidade: float
    comprado: bool


class ItemDetalheOut(ItemOut):
    produto_nome: str
    produto_marca: Optional[str]
    unidade_medida: str


class ListaOut(BaseModel):
    id: int
    nome: str
    criada_em: datetime
    itens: list[ItemDetalheOut]


class MercadoTotalOut(BaseModel):
    supermercado_id: int
    supermercado_nome: str
    total: float = Field(description="Soma de preço mais recente × quantidade dos itens encontrados.")
    itens_encontrados: int
    itens_faltando: int
    completo: bool


class ComparacaoListaOut(BaseModel):
    lista_id: int
    lista_nome: str
    total_itens: int
    referencia: str = Field(
        description="Como o total e a economia foram calculados (transparência para o usuário)."
    )
    melhor_opcao: Optional[MercadoTotalOut]
    economia: float = Field(description="Diferença entre o mercado completo mais caro e o mais barato.")
    economia_percentual: float
    supermercados: list[MercadoTotalOut]
