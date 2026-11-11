"""Formato único das respostas de erro (documentado no Swagger)."""
from typing import Optional

from pydantic import BaseModel


class DetalheErro(BaseModel):
    campo: str
    mensagem: str


class Erro(BaseModel):
    codigo: str
    mensagem: str
    detalhes: Optional[list[DetalheErro]] = None


class ErroOut(BaseModel):
    erro: Erro


_EXEMPLOS = {
    400: ("Requisição inválida", "requisicao_invalida", "Informe ao menos um campo para atualizar."),
    404: ("Registro não encontrado", "nao_encontrado", "Produto 999 não encontrado(a)."),
    409: ("Conflito com dados existentes", "registro_duplicado", "Já existe um registro com esses dados."),
    422: ("Dados inválidos ou regra de negócio violada", "validacao", "Dados de entrada inválidos."),
}


def respostas(*status: int) -> dict:
    """Monta o parâmetro `responses` das rotas com o schema e um exemplo de cada erro."""
    resultado = {}
    for s in status:
        descricao, codigo, mensagem = _EXEMPLOS[s]
        resultado[s] = {
            "model": ErroOut,
            "description": descricao,
            "content": {
                "application/json": {"example": {"erro": {"codigo": codigo, "mensagem": mensagem}}}
            },
        }
    return resultado
