from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema, UpdateSchema

Unidade = Literal["un", "kg", "g", "l", "ml"]


class ProdutoCreate(CreateSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nome": "Feijão Carioca 1kg",
                    "marca": "Kicaldo",
                    "unidade_medida": "kg",
                    "codigo_barras": "7896006744115",
                    "categoria_id": 1,
                }
            ]
        }
    )

    nome: str = Field(min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Unidade = Field(description="Uma de: un, kg, g, l, ml.")
    codigo_barras: Optional[str] = Field(
        default=None, pattern=r"^[0-9]{8,14}$", description="EAN/GTIN com 8 a 14 dígitos."
    )
    categoria_id: int = Field(gt=0, description="Precisa ser uma categoria existente.")


class ProdutoUpdate(UpdateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"marca": "Camil", "unidade_medida": "kg"}]})

    nao_nulos = ("nome", "unidade_medida", "categoria_id")
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    marca: Optional[str] = Field(default=None, max_length=60)
    unidade_medida: Optional[Unidade] = None
    codigo_barras: Optional[str] = Field(default=None, pattern=r"^[0-9]{8,14}$")
    categoria_id: Optional[int] = Field(default=None, gt=0)


class ProdutoOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nome": "Arroz Branco Tipo 1 5kg",
                    "marca": "Tio João",
                    "unidade_medida": "un",
                    "codigo_barras": "7893500020110",
                    "categoria_id": 1,
                }
            ]
        },
    )

    id: int
    nome: str
    marca: Optional[str]
    unidade_medida: str
    codigo_barras: Optional[str]
    categoria_id: int
