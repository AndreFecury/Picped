from fastapi import APIRouter, Depends

from app.dependencies import get_health_service
from app.services.health_service import HealthService

router = APIRouter(tags=["Saúde"])


@router.get("/health")
def health(service: HealthService = Depends(get_health_service)):
    return service.status()
