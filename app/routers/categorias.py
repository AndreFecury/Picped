from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_categoria_service
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaOut])
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.listar(limit, offset)


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def criar(payload: CategoriaCreate, service: CategoriaService = Depends(get_categoria_service)):
    return service.criar(payload.model_dump())


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obter(categoria_id: int, service: CategoriaService = Depends(get_categoria_service)):
    return service.obter(categoria_id)


@router.patch("/{categoria_id}", response_model=CategoriaOut)
def atualizar(
    categoria_id: int,
    payload: CategoriaUpdate,
    service: CategoriaService = Depends(get_categoria_service),
):
    return service.atualizar(categoria_id, payload.model_dump(exclude_unset=True))


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(categoria_id: int, service: CategoriaService = Depends(get_categoria_service)):
    service.deletar(categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
