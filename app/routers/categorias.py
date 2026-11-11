from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_categoria_service
from app.schemas.base import IdPath
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.schemas.erro import respostas
from app.services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorias"], responses=respostas(422))


@router.get("", response_model=list[CategoriaOut], summary="Listar categorias")
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    responses=respostas(400, 409),
)
def criar(payload: CategoriaCreate, service: CategoriaService = Depends(get_categoria_service)):
    return service.criar(payload.model_dump())


@router.get("/{categoria_id}", response_model=CategoriaOut, summary="Obter categoria", responses=respostas(404))
def obter(categoria_id: IdPath, service: CategoriaService = Depends(get_categoria_service)):
    return service.obter(categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaOut,
    summary="Substituir categoria",
    responses=respostas(400, 404, 409),
)
def substituir(
    categoria_id: IdPath,
    payload: CategoriaCreate,
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.substituir(categoria_id, payload.model_dump())


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaOut,
    summary="Atualizar parte da categoria",
    responses=respostas(400, 404, 409),
)
def atualizar(
    categoria_id: IdPath,
    payload: CategoriaUpdate,
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.atualizar(categoria_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    description="Retorna 409 se houver produtos usando a categoria.",
    responses=respostas(404, 409),
)
def deletar(categoria_id: IdPath, service: CategoriaService = Depends(get_categoria_service)):
    service.deletar(categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
