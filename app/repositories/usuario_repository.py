from app.domain.models import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    table = "usuario"
    model = Usuario
    columns = ("nome", "email", "senha_hash", "criado_em")
