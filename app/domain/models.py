"""Camada Domain: entidades do negócio (sem dependência de framework ou banco)."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Categoria:
    id: int
    nome: str


@dataclass
class Produto:
    id: int
    nome: str
    marca: Optional[str]
    unidade_medida: str
    codigo_barras: Optional[str]
    categoria_id: int


@dataclass
class Supermercado:
    id: int
    nome: str
    cidade: str
    bairro: str
    endereco: Optional[str]
    latitude: Decimal
    longitude: Decimal
    raio_metros: int
    ativo: bool


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha_hash: str
    criado_em: datetime


@dataclass
class Preco:
    id: int
    produto_id: int
    supermercado_id: int
    usuario_id: int
    valor: Decimal
    coletado_em: datetime
    distancia_metros: Optional[int]


@dataclass
class ListaCompras:
    id: int
    usuario_id: int
    nome: str
    criada_em: datetime


@dataclass
class ItemLista:
    id: int
    lista_id: int
    produto_id: int
    quantidade: Decimal
    comprado: bool
