from sqlalchemy import text

from app.domain.models import ItemLista, ListaCompras
from app.repositories.base import BaseRepository


class ListaRepository(BaseRepository[ListaCompras]):
    table = "lista_compras"
    model = ListaCompras
    columns = ("usuario_id", "nome", "criada_em")

    def listar_do_usuario(self, usuario_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
        """Listas do usuário com a quantidade de itens (mais recentes primeiro)."""
        sql = text(
            """
            SELECT l.id, l.usuario_id, l.nome, l.criada_em, COUNT(i.id)::int AS total_itens
            FROM lista_compras l
            LEFT JOIN item_lista i ON i.lista_id = l.id
            WHERE l.usuario_id = :usuario_id
            GROUP BY l.id
            ORDER BY l.criada_em DESC, l.id DESC
            LIMIT :limit OFFSET :offset
            """
        )
        rows = self.conn.execute(sql, {"usuario_id": usuario_id, "limit": limit, "offset": offset})
        return [dict(r._mapping) for r in rows]

    def itens_detalhados(self, lista_id: int) -> list[dict]:
        sql = text(
            """
            SELECT i.id, i.lista_id, i.produto_id, i.quantidade, i.comprado,
                   p.nome AS produto_nome, p.marca AS produto_marca, p.unidade_medida
            FROM item_lista i
            JOIN produto p ON p.id = i.produto_id
            WHERE i.lista_id = :lista_id
            ORDER BY p.nome
            """
        )
        return [dict(r._mapping) for r in self.conn.execute(sql, {"lista_id": lista_id})]

    def precos_dos_itens(self, lista_id: int) -> list[dict]:
        """Preço mais recente de cada item da lista em cada supermercado ativo."""
        sql = text(
            """
            SELECT DISTINCT ON (i.produto_id, pr.supermercado_id)
                   i.produto_id, i.quantidade, pr.supermercado_id, s.nome AS supermercado_nome,
                   pr.valor
            FROM item_lista i
            JOIN preco pr ON pr.produto_id = i.produto_id
            JOIN supermercado s ON s.id = pr.supermercado_id AND s.ativo
            WHERE i.lista_id = :lista_id
            ORDER BY i.produto_id, pr.supermercado_id, pr.coletado_em DESC
            """
        )
        return [dict(r._mapping) for r in self.conn.execute(sql, {"lista_id": lista_id})]


class ItemListaRepository(BaseRepository[ItemLista]):
    table = "item_lista"
    model = ItemLista
    columns = ("lista_id", "produto_id", "quantidade", "comprado")

    def buscar_na_lista(self, lista_id: int, item_id: int) -> ItemLista | None:
        sql = text(f"SELECT {self._select} FROM item_lista WHERE id = :id AND lista_id = :lista_id")
        row = self.conn.execute(sql, {"id": item_id, "lista_id": lista_id}).one_or_none()
        return self._para_modelo(row) if row else None
