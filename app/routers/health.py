from fastapi import APIRouter, Depends

from app.dependencies import get_health_service
from app.services.health_service import HealthService

router = APIRouter(tags=["Saúde"])


@router.get(
    "/health",
    summary="Verificar se a API e o banco estão no ar",
    responses={
        200: {"content": {"application/json": {"example": {"status": "ok", "banco": "ok"}}}},
        503: {"description": "Banco de dados indisponível."},
    },
)
def health(service: HealthService = Depends(get_health_service)):
    return service.status()
