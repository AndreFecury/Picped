"""
Camada Repository/DAO: único lugar que conversa com o banco.
Todas as consultas são parametrizadas (valores sempre via bind params, nunca concatenados).
Nomes de tabela/colunas vêm de constantes das classes filhas, nunca da entrada do usuário.
"""
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import text
from sqlalchemy.engine import Connection

T = TypeVar("T")


class BaseRepository(Generic[T]):
    table: str
    model: type
    columns: tuple[str, ...]  # colunas graváveis (sem o id)

    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    @property
    def _select(self) -> str:
        return ", ".join(("id", *self.columns))

    def _para_modelo(self, row) -> T:
        return self.model(**row._mapping)

    def listar(self, limit: int = 50, offset: int = 0) -> list[T]:
        sql = text(f"SELECT {self._select} FROM {self.table} ORDER BY id LIMIT :limit OFFSET :offset")
        rows = self.conn.execute(sql, {"limit": limit, "offset": offset})
        return [self._para_modelo(r) for r in rows]

    def buscar_por_id(self, id_: int) -> Optional[T]:
        sql = text(f"SELECT {self._select} FROM {self.table} WHERE id = :id")
        row = self.conn.execute(sql, {"id": id_}).one_or_none()
        return self._para_modelo(row) if row else None

    def existe(self, id_: int) -> bool:
        sql = text(f"SELECT 1 FROM {self.table} WHERE id = :id")
        return self.conn.execute(sql, {"id": id_}).first() is not None

    def criar(self, dados: dict[str, Any]) -> T:
        # None = "não informado": a coluna usa o DEFAULT do banco (ou NULL)
        dados = {k: v for k, v in dados.items() if k in self.columns and v is not None}
        colunas = ", ".join(dados)
        valores = ", ".join(f":{c}" for c in dados)
        sql = text(f"INSERT INTO {self.table} ({colunas}) VALUES ({valores}) RETURNING {self._select}")
        row = self.conn.execute(sql, dados).one()
        self.conn.commit()
        return self._para_modelo(row)

    def atualizar(self, id_: int, dados: dict[str, Any]) -> Optional[T]:
        dados = {k: v for k, v in dados.items() if k in self.columns}
        if not dados:
            return self.buscar_por_id(id_)
        sets = ", ".join(f"{c} = :{c}" for c in dados)
        sql = text(f"UPDATE {self.table} SET {sets} WHERE id = :pk RETURNING {self._select}")
        row = self.conn.execute(sql, {**dados, "pk": id_}).one_or_none()
        self.conn.commit()
        return self._para_modelo(row) if row else None

    def deletar(self, id_: int) -> bool:
        resultado = self.conn.execute(text(f"DELETE FROM {self.table} WHERE id = :id"), {"id": id_})
        self.conn.commit()
        return resultado.rowcount > 0
