from app.services.base import BaseService, normalizar_texto


class CategoriaService(BaseService):
    entidade = "Categoria"

    def criar(self, dados):
        dados["nome"] = normalizar_texto(dados["nome"])
        return super().criar(dados)

    def atualizar(self, id_, dados):
        if dados.get("nome"):
            dados["nome"] = normalizar_texto(dados["nome"])
        return super().atualizar(id_, dados)
