from typing import Optional

from sqlalchemy import text

from app.domain.models import Preco
from app.repositories.base import BaseRepository


class PrecoRepository(BaseRepository[Preco]):
    table = "preco"
    model = Preco
    columns = ("produto_id", "supermercado_id", "usuario_id", "valor", "coletado_em", "distancia_metros")

    def listar(
        self,
        limit: int = 50,
        offset: int = 0,
        produto_id: Optional[int] = None,
        supermercado_id: Optional[int] = None,
    ) -> list[Preco]:
        filtros: list[str] = []
        params: dict = {"limit": limit, "offset": offset}
        if produto_id is not None:
            filtros.append("produto_id = :produto_id")
            params["produto_id"] = produto_id
        if supermercado_id is not None:
            filtros.append("supermercado_id = :supermercado_id")
            params["supermercado_id"] = supermercado_id
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        sql = text(
            f"SELECT {self._select} FROM {self.table} {where} "
            "ORDER BY coletado_em DESC, id DESC LIMIT :limit OFFSET :offset"
        )
        return [self._para_modelo(r) for r in self.conn.execute(sql, params)]

    def ultimos_por_supermercado(self, produto_id: int) -> list[dict]:
        """Preço mais recente do produto em cada supermercado."""
        sql = text(
            """
            SELECT DISTINCT ON (pr.supermercado_id)
                   s.id AS supermercado_id, s.nome AS supermercado_nome,
                   pr.valor, pr.coletado_em
            FROM preco pr
            JOIN supermercado s ON s.id = pr.supermercado_id
            WHERE pr.produto_id = :produto_id
            ORDER BY pr.supermercado_id, pr.coletado_em DESC
            """
        )
        return [dict(r._mapping) for r in self.conn.execute(sql, {"produto_id": produto_id})]

    def historico(self, produto_id: int) -> list[dict]:
        """Todos os preços registrados do produto (mais antigos primeiro), com o nome do mercado."""
        sql = text(
            """
            SELECT pr.valor, pr.coletado_em, s.id AS supermercado_id, s.nome AS supermercado_nome
            FROM preco pr
            JOIN supermercado s ON s.id = pr.supermercado_id
            WHERE pr.produto_id = :produto_id
            ORDER BY pr.coletado_em, pr.id
            """
        )
        return [dict(r._mapping) for r in self.conn.execute(sql, {"produto_id": produto_id})]
