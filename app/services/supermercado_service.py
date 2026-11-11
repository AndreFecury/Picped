from app.repositories.supermercado_repository import SupermercadoRepository
from app.services.base import BaseService, normalizar_texto


class SupermercadoService(BaseService):
    entidade = "Supermercado"

    def __init__(self, repo: SupermercadoRepository) -> None:
        super().__init__(repo)

    @staticmethod
    def _normalizar(dados: dict) -> dict:
        for campo in ("nome", "cidade", "bairro", "endereco"):
            if dados.get(campo):
                dados[campo] = normalizar_texto(dados[campo])
        return dados

    def criar(self, dados):
        return super().criar(self._normalizar(dados))

    def substituir(self, id_, dados):
        return super().substituir(id_, self._normalizar(dados))

    def atualizar(self, id_, dados):
        return super().atualizar(id_, self._normalizar(dados))

    def proximos(self, latitude: float, longitude: float) -> list[dict]:
        """Supermercados cujo raio contém a posição do usuário (do mais perto ao mais longe)."""
        return self.repo.proximos(latitude, longitude)
