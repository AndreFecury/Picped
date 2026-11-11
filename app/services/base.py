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

    def listar(self, limit: int = 50, offset: int = 0):
        return self.repo.listar(limit, offset)

    def obter(self, id_: int):
        registro = self.repo.buscar_por_id(id_)
        if registro is None:
            raise NotFoundError(f"{self.entidade} {id_} não encontrado(a).")
        return registro

    def criar(self, dados: dict[str, Any]):
        return self.repo.criar(dados)

    @staticmethod
    def exigir_campos(dados: dict[str, Any]) -> None:
        """PATCH sem nenhum campo não tem o que atualizar: requisição inválida (400)."""
        if not dados:
            raise BadRequestError("Informe ao menos um campo para atualizar.")

    def atualizar(self, id_: int, dados: dict[str, Any]):
        self.obter(id_)  # 404 se não existir
        self.exigir_campos(dados)
        return self.repo.atualizar(id_, dados)

    def deletar(self, id_: int) -> None:
        if not self.repo.deletar(id_):
            raise NotFoundError(f"{self.entidade} {id_} não encontrado(a).")
