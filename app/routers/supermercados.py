from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.dependencies import get_supermercado_service
from app.schemas.erro import respostas
from app.schemas.supermercado import (
    SupermercadoCreate,
    SupermercadoOut,
    SupermercadoProximoOut,
    SupermercadoUpdate,
)
from app.services.supermercado_service import SupermercadoService

router = APIRouter(prefix="/supermercados", tags=["Supermercados"])

SupermercadoId = Path(gt=0, description="ID do supermercado.", examples=[1])


@router.get("", response_model=list[SupermercadoOut], summary="Listar supermercados", responses=respostas(422))
def listar(
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.listar(limit, offset)


@router.get(
    "/proximos",
    response_model=list[SupermercadoProximoOut],
    summary="Supermercados próximos da localização do usuário",
    responses=respostas(422),
)
def proximos(
    latitude: float = Query(ge=-90, le=90, examples=[-3.0905]),
    longitude: float = Query(ge=-180, le=180, examples=[-60.0185]),
    service: SupermercadoService = Depends(get_supermercado_service),
):
    """Identifica o supermercado onde o usuário está a partir da localização do celular."""
    return service.proximos(latitude, longitude)


@router.post(
    "",
    response_model=SupermercadoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar supermercado",
    responses=respostas(400, 409, 422),
)
def criar(payload: SupermercadoCreate, service: SupermercadoService = Depends(get_supermercado_service)):
    return service.criar(payload.model_dump())


@router.get(
    "/{supermercado_id}",
    response_model=SupermercadoOut,
    summary="Buscar supermercado",
    responses=respostas(404, 422),
)
def obter(
    supermercado_id: int = SupermercadoId,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.obter(supermercado_id)


@router.patch(
    "/{supermercado_id}",
    response_model=SupermercadoOut,
    summary="Atualizar supermercado (parcial)",
    responses=respostas(400, 404, 409, 422),
)
def atualizar(
    payload: SupermercadoUpdate,
    supermercado_id: int = SupermercadoId,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    return service.atualizar(supermercado_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{supermercado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir supermercado",
    response_class=Response,
    responses=respostas(404, 409, 422),
)
def deletar(
    supermercado_id: int = SupermercadoId,
    service: SupermercadoService = Depends(get_supermercado_service),
):
    """Retorna 409 se houver preços registrados no supermercado (prefira desativar com `ativo: false`)."""
    service.deletar(supermercado_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
