from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_supermercado_service
from app.schemas.supermercado import (
    SupermercadoCreate,
    SupermercadoOut,
    SupermercadoProximoOut,
    SupermercadoUpdate,
)
from app.services.supermercado_service import SupermercadoService

router = APIRouter(prefix="/supermercados", tags=["Supermercados"])


@router.get("", response_model=list[SupermercadoOut])
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.listar(limit, offset)


@router.get("/proximos", response_model=list[SupermercadoProximoOut])
def proximos(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    """Identifica o supermercado onde o usuário está a partir da localização do celular."""
    return service.proximos(latitude, longitude)


@router.post("", response_model=SupermercadoOut, status_code=status.HTTP_201_CREATED)
def criar(payload: SupermercadoCreate, service: SupermercadoService = Depends(get_supermercado_service)):
    return service.criar(payload.model_dump())


@router.get("/{supermercado_id}", response_model=SupermercadoOut)
def obter(supermercado_id: int, service: SupermercadoService = Depends(get_supermercado_service)):
    return service.obter(supermercado_id)


@router.patch("/{supermercado_id}", response_model=SupermercadoOut)
def atualizar(
    supermercado_id: int,
    payload: SupermercadoUpdate,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.atualizar(supermercado_id, payload.model_dump(exclude_unset=True))


@router.delete("/{supermercado_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(supermercado_id: int, service: SupermercadoService = Depends(get_supermercado_service)):
    service.deletar(supermercado_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
