from app.domain.models import Categoria
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    table = "categoria"
    model = Categoria
    columns = ("nome",)
