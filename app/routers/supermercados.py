from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_supermercado_service
from app.schemas.base import IdPath
from app.schemas.erro import respostas
from app.schemas.supermercado import (
    SupermercadoCreate,
    SupermercadoOut,
    SupermercadoProximoOut,
    SupermercadoUpdate,
)
from app.services.supermercado_service import SupermercadoService

router = APIRouter(prefix="/supermercados", tags=["Supermercados"], responses=respostas(422))


@router.get("", response_model=list[SupermercadoOut], summary="Listar supermercados")
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.listar(limit, offset)


@router.get("/proximos", response_model=list[SupermercadoProximoOut], summary="Supermercados próximos")
def proximos(
    latitude: float = Query(ge=-90, le=90, examples=[-3.1115]),
    longitude: float = Query(ge=-180, le=180, examples=[-60.0128]),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    """Identifica o supermercado onde o usuário está a partir da localização do celular."""
    return service.proximos(latitude, longitude)


@router.post(
    "",
    response_model=SupermercadoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar supermercado",
    responses=respostas(400, 409),
)
def criar(payload: SupermercadoCreate, service: SupermercadoService = Depends(get_supermercado_service)):
    return service.criar(payload.model_dump())


@router.get(
    "/{supermercado_id}", response_model=SupermercadoOut, summary="Obter supermercado", responses=respostas(404)
)
def obter(supermercado_id: IdPath, service: SupermercadoService = Depends(get_supermercado_service)):
    return service.obter(supermercado_id)


@router.put(
    "/{supermercado_id}",
    response_model=SupermercadoOut,
    summary="Substituir supermercado",
    responses=respostas(400, 404, 409),
)
def substituir(
    supermercado_id: IdPath,
    payload: SupermercadoCreate,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.substituir(supermercado_id, payload.model_dump())


@router.patch(
    "/{supermercado_id}",
    response_model=SupermercadoOut,
    summary="Atualizar parte do supermercado",
    responses=respostas(400, 404, 409),
)
def atualizar(
    supermercado_id: IdPath,
    payload: SupermercadoUpdate,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.atualizar(supermercado_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{supermercado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir supermercado",
    description="Retorna 409 se o supermercado tiver preços registrados (desative com ativo=false).",
    responses=respostas(404, 409),
)
def deletar(supermercado_id: IdPath, service: SupermercadoService = Depends(get_supermercado_service)):
    service.deletar(supermercado_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
