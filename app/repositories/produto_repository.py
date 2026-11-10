from app.domain.models import Produto
from app.repositories.base import BaseRepository


class ProdutoRepository(BaseRepository[Produto]):
    table = "produto"
    model = Produto
    columns = ("nome", "marca", "unidade_medida", "codigo_barras", "categoria_id")
