from sqlalchemy import text

from app.domain.models import Supermercado
from app.repositories.base import BaseRepository


class SupermercadoRepository(BaseRepository[Supermercado]):
    table = "supermercado"
    model = Supermercado
    columns = ("nome", "cidade", "bairro", "endereco", "latitude", "longitude", "raio_metros", "ativo")

    def proximos(self, latitude: float, longitude: float) -> list[dict]:
        """Usa a função SQL supermercados_proximos (Haversine) criada no schema.sql."""
        sql = text("SELECT id, nome, distancia_metros FROM supermercados_proximos(:lat, :lon)")
        rows = self.conn.execute(sql, {"lat": latitude, "lon": longitude})
        return [dict(r._mapping) for r in rows]
