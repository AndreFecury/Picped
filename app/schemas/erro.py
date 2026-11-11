"""Formato único das respostas de erro, usado para documentar cada rota no Swagger."""
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErroDetalhe(BaseModel):
    campo: str = Field(examples=["nome"])
    mensagem: str = Field(examples=["String should have at least 2 characters"])


class ErroCorpo(BaseModel):
    codigo: str = Field(examples=["nao_encontrado"])
    mensagem: str = Field(examples=["Produto 99 não encontrado(a)."])
    detalhes: Optional[list[ErroDetalhe]] = None


class ErroOut(BaseModel):
    erro: ErroCorpo


_EXEMPLOS: dict[int, tuple[str, dict[str, Any]]] = {
    400: (
        "Requisição mal formada (JSON inválido ou PATCH sem nenhum campo).",
        {"erro": {"codigo": "requisicao_invalida", "mensagem": "Informe ao menos um campo para atualizar."}},
    ),
    404: (
        "Registro não encontrado.",
        {"erro": {"codigo": "nao_encontrado", "mensagem": "Registro 99 não encontrado(a)."}},
    ),
    409: (
        "Conflito com dados existentes (duplicidade ou registro em uso).",
        {"erro": {"codigo": "registro_duplicado", "mensagem": "Já existe um registro com esses dados."}},
    ),
    422: (
        "Dados inválidos (validação do schema) ou regra de negócio violada.",
        {
            "erro": {
                "codigo": "validacao",
                "mensagem": "Dados de entrada inválidos.",
                "detalhes": [{"campo": "nome", "mensagem": "String should have at least 2 characters"}],
            }
        },
    ),
}


def respostas(*status: int) -> dict[int | str, dict[str, Any]]:
    """Monta o parâmetro `responses` das rotas com o schema de erro e um exemplo para cada status."""
    return {
        s: {
            "model": ErroOut,
            "description": _EXEMPLOS[s][0],
            "content": {"application/json": {"example": _EXEMPLOS[s][1]}},
        }
        for s in status
    }
