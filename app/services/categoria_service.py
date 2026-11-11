from app.services.base import BaseService, normalizar_texto


class CategoriaService(BaseService):
    entidade = "Categoria"

    @staticmethod
    def _normalizar(dados: dict) -> dict:
        if dados.get("nome"):
            dados["nome"] = normalizar_texto(dados["nome"])
        return dados

    def criar(self, dados):
        return super().criar(self._normalizar(dados))

    def substituir(self, id_, dados):
        return super().substituir(id_, self._normalizar(dados))

    def atualizar(self, id_, dados):
        return super().atualizar(id_, self._normalizar(dados))
