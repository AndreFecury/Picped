from sqlalchemy import text

from app.domain.models import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    table = "usuario"
    model = Usuario
    columns = ("nome", "email", "senha_hash", "criado_em")

    def buscar_por_email(self, email: str) -> Usuario | None:
        sql = text(f"SELECT {self._select} FROM usuario WHERE email = :email")
        row = self.conn.execute(sql, {"email": email.lower()}).one_or_none()
        return self._para_modelo(row) if row else None

    def excluir_com_dados(self, id_: int) -> None:
        # as duas operações na mesma transação: ou apaga tudo ou nada
        self.conn.execute(text("DELETE FROM preco WHERE usuario_id = :id"), {"id": id_})
        self.conn.execute(text("DELETE FROM usuario WHERE id = :id"), {"id": id_})
        self.conn.commit()
