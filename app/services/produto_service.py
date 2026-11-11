from app.core.exceptions import BusinessRuleError
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.services.base import BaseService, normalizar_texto


class ProdutoService(BaseService):
    entidade = "Produto"

    def __init__(self, repo: ProdutoRepository, categorias: CategoriaRepository) -> None:
        super().__init__(repo)
        self.categorias = categorias

    def _validar(self, dados: dict) -> dict:
        """Regra: a categoria precisa existir. Também normaliza os textos."""
        for campo in ("nome", "marca"):
            if dados.get(campo):
                dados[campo] = normalizar_texto(dados[campo])
        categoria_id = dados.get("categoria_id")
        if categoria_id is not None and not self.categorias.existe(categoria_id):
            raise BusinessRuleError(f"A categoria {categoria_id} não existe.")
        return dados

    def criar(self, dados):
        return super().criar(self._validar(dados))

    def substituir(self, id_, dados):
        self.obter(id_)
        return super().substituir(id_, self._validar(dados))

    def atualizar(self, id_, dados):
        if dados:
            self.obter(id_)  # 404 antes de validar regras
        return super().atualizar(id_, self._validar(dados))
