from typing import Optional

from sqlalchemy import text

from app.domain.models import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    table = "usuario"
    model = Usuario
    columns = ("nome", "email", "senha_hash", "criado_em")

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        sql = text(f"SELECT {self._select} FROM {self.table} WHERE LOWER(email) = LOWER(:email)")
        row = self.conn.execute(sql, {"email": email}).one_or_none()
        return self._para_modelo(row) if row else None
