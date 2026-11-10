from app.repositories.supermercado_repository import SupermercadoRepository
from app.services.base import BaseService, normalizar_texto


class SupermercadoService(BaseService):
    entidade = "Supermercado"

    def __init__(self, repo: SupermercadoRepository) -> None:
        super().__init__(repo)

    @staticmethod
    def _normalizar(dados: dict) -> None:
        for campo in ("nome", "cidade", "bairro", "endereco"):
            if dados.get(campo):
                dados[campo] = normalizar_texto(dados[campo])

    def criar(self, dados):
        self._normalizar(dados)
        return super().criar(dados)

    def atualizar(self, id_, dados):
        self._normalizar(dados)
        return super().atualizar(id_, dados)

    def proximos(self, latitude: float, longitude: float) -> list[dict]:
        """Supermercados cujo raio contém a posição do usuário (do mais perto ao mais longe)."""
        return self.repo.proximos(latitude, longitude)
