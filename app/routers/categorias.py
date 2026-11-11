from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.dependencies import get_categoria_service
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.schemas.erro import respostas
from app.services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorias"])

CategoriaId = Path(gt=0, description="ID da categoria.", examples=[1])


@router.get("", response_model=list[CategoriaOut], summary="Listar categorias", responses=respostas(422))
def listar(
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    responses=respostas(400, 409, 422),
)
def criar(payload: CategoriaCreate, service: CategoriaService = Depends(get_categoria_service)):
    return service.criar(payload.model_dump())


@router.get(
    "/{categoria_id}", response_model=CategoriaOut, summary="Buscar categoria", responses=respostas(404, 422)
)
def obter(categoria_id: int = CategoriaId, service: CategoriaService = Depends(get_categoria_service)):
    return service.obter(categoria_id)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaOut,
    summary="Atualizar categoria (parcial)",
    responses=respostas(400, 404, 409, 422),
)
def atualizar(
    payload: CategoriaUpdate,
    categoria_id: int = CategoriaId,
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.atualizar(categoria_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    response_class=Response,
    responses=respostas(404, 409, 422),
)
def deletar(categoria_id: int = CategoriaId, service: CategoriaService = Depends(get_categoria_service)):
    """Retorna 409 se houver produtos usando a categoria."""
    service.deletar(categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
