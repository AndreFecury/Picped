from app.core.exceptions import BusinessRuleError
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.services.base import BaseService, normalizar_texto


class ProdutoService(BaseService):
    entidade = "Produto"

    def __init__(self, repo: ProdutoRepository, categorias: CategoriaRepository) -> None:
        super().__init__(repo)
        self.categorias = categorias

    def _validar(self, dados: dict) -> None:
        for campo in ("nome", "marca"):
            if dados.get(campo):
                dados[campo] = normalizar_texto(dados[campo])
        categoria_id = dados.get("categoria_id")
        if categoria_id is not None and not self.categorias.existe(categoria_id):
            raise BusinessRuleError(f"A categoria {categoria_id} não existe.")

    def listar(self, limit=50, offset=0, busca=None, codigo_barras=None, categoria_id=None):
        busca = normalizar_texto(busca) if busca else None
        return self.repo.listar(limit, offset, busca, codigo_barras, categoria_id)

    def criar(self, dados):
        self._validar(dados)
        return super().criar(dados)

    def atualizar(self, id_, dados):
        self.obter(id_)
        self.exigir_campos(dados)
        self._validar(dados)
        return self.repo.atualizar(id_, dados)
