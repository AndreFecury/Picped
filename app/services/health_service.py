from app.core.config import get_settings
from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repo: HealthRepository) -> None:
        self.repo = repo

    def status(self) -> dict:
        # se o banco estiver fora, o OperationalError vira 503 no handler central
        self.repo.ping()
        return {"status": "ok", "banco": "ok", "versao": get_settings().commit}
