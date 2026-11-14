from typing import Optional

from sqlalchemy import text

from app.domain.models import Produto
from app.repositories.base import BaseRepository


class ProdutoRepository(BaseRepository[Produto]):
    table = "produto"
    model = Produto
    columns = ("nome", "marca", "unidade_medida", "codigo_barras", "categoria_id")

    def listar(
        self,
        limit: int = 50,
        offset: int = 0,
        busca: Optional[str] = None,
        codigo_barras: Optional[str] = None,
        categoria_id: Optional[int] = None,
    ) -> list[Produto]:
        filtros: list[str] = []
        params: dict = {"limit": limit, "offset": offset}
        if busca:
            # o termo vai como parâmetro; os curingas % são adicionados aqui, não concatenados no SQL
            filtros.append("(LOWER(nome) LIKE :busca OR LOWER(COALESCE(marca, '')) LIKE :busca)")
            params["busca"] = f"%{busca.lower()}%"
        if codigo_barras:
            filtros.append("codigo_barras = :codigo_barras")
            params["codigo_barras"] = codigo_barras
        if categoria_id is not None:
            filtros.append("categoria_id = :categoria_id")
            params["categoria_id"] = categoria_id
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        sql = text(f"SELECT {self._select} FROM produto {where} ORDER BY nome LIMIT :limit OFFSET :offset")
        return [self._para_modelo(r) for r in self.conn.execute(sql, params)]
