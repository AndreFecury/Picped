"""
Camada Service: regras de negócio. Não conhece HTTP nem SQL:
recebe dados já validados, aplica as regras e usa os repositories.
"""
from typing import Any

from app.core.exceptions import BadRequestError, NotFoundError


def normalizar_texto(valor: str) -> str:
    """Remove espaços extras (início, fim e repetidos no meio)."""
    return " ".join(valor.split())


class BaseService:
    entidade = "Registro"

    def __init__(self, repo) -> None:
        self.repo = repo

    def _nao_encontrado(self, id_: int) -> NotFoundError:
        return NotFoundError(f"{self.entidade} {id_} não encontrado(a).")

    def listar(self, limit: int = 50, offset: int = 0):
        return self.repo.listar(limit, offset)

    def obter(self, id_: int):
        registro = self.repo.buscar_por_id(id_)
        if registro is None:
            raise self._nao_encontrado(id_)
        return registro

    def criar(self, dados: dict[str, Any]):
        return self.repo.criar(dados)

    def substituir(self, id_: int, dados: dict[str, Any]):
        """PUT: troca todos os campos editáveis do registro."""
        self.obter(id_)  # 404 se não existir
        return self.repo.atualizar(id_, dados)

    @staticmethod
    def exigir_campos(dados: dict[str, Any]) -> None:
        """PATCH sem nenhum campo não tem o que atualizar: requisição inválida (400)."""
        if not dados:
            raise BadRequestError("Informe ao menos um campo para atualizar.")

    def atualizar(self, id_: int, dados: dict[str, Any]):
        """PATCH: altera só os campos enviados."""
        self.exigir_campos(dados)
        self.obter(id_)  # 404 se não existir
        return self.repo.atualizar(id_, dados)

    def deletar(self, id_: int) -> None:
        if not self.repo.deletar(id_):
            raise self._nao_encontrado(id_)
