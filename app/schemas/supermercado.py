from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from app.schemas.base import EntradaSchema, UpdateSchema

_EXEMPLO = {
    "nome": "Assaí Atacadista",
    "cidade": "Manaus",
    "bairro": "Japiim",
    "endereco": "Av. Rodrigo Otávio, 1000",
    "latitude": -3.124500,
    "longitude": -59.985300,
    "raio_metros": 120,
    "ativo": True,
}


class SupermercadoCreate(EntradaSchema):
    """Usado no POST e no PUT (substituição completa)."""

    model_config = ConfigDict(json_schema_extra={"examples": [_EXEMPLO]})
    nome: str = Field(min_length=2, max_length=100)
    cidade: str = Field(min_length=2, max_length=80)
    bairro: str = Field(min_length=2, max_length=80)
    endereco: Optional[str] = Field(default=None, max_length=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    raio_metros: int = Field(default=80, gt=0, le=5000, strict=True, description="Tolerância do GPS (m)")
    ativo: StrictBool = True


class SupermercadoUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"raio_metros": 150, "ativo": False}]})
    nao_nulos = ("nome", "cidade", "bairro", "latitude", "longitude", "raio_metros", "ativo")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    cidade: Optional[str] = Field(default=None, min_length=2, max_length=80)
    bairro: Optional[str] = Field(default=None, min_length=2, max_length=80)
    endereco: Optional[str] = Field(default=None, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    raio_metros: Optional[int] = Field(default=None, gt=0, le=5000, strict=True)
    ativo: Optional[StrictBool] = None


class SupermercadoOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [{"id": 6, **_EXEMPLO}]}
    )
    id: int
    nome: str
    cidade: str
    bairro: str
    endereco: Optional[str]
    latitude: float
    longitude: float
    raio_metros: int
    ativo: bool


class SupermercadoProximoOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"id": 2, "nome": "Carvalho", "distancia_metros": 35}]}
    )
    id: int
    nome: str
    distancia_metros: int
