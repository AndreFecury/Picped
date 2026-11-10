from sqlalchemy import text
from sqlalchemy.engine import Connection


class HealthRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def ping(self) -> bool:
        return self.conn.execute(text("SELECT 1")).scalar_one() == 1
