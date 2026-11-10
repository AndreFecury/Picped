from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_preco_service
from app.schemas.preco import PrecoCreate, PrecoOut, PrecoUpdate
from app.services.preco_service import PrecoService

router = APIRouter(prefix="/precos", tags=["Preços"])


@router.get("", response_model=list[PrecoOut])
def listar(
    produto_id: Optional[int] = Query(None, gt=0),
    supermercado_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: PrecoService = Depends(get_preco_service),
):
    return service.listar(limit, offset, produto_id, supermercado_id)


@router.post("", response_model=PrecoOut, status_code=status.HTTP_201_CREATED)
def criar(payload: PrecoCreate, service: PrecoService = Depends(get_preco_service)):
    return service.criar(payload.model_dump())


@router.get("/{preco_id}", response_model=PrecoOut)
def obter(preco_id: int, service: PrecoService = Depends(get_preco_service)):
    return service.obter(preco_id)


@router.patch("/{preco_id}", response_model=PrecoOut)
def atualizar(preco_id: int, payload: PrecoUpdate, service: PrecoService = Depends(get_preco_service)):
    return service.atualizar(preco_id, payload.model_dump(exclude_unset=True))


@router.delete("/{preco_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(preco_id: int, service: PrecoService = Depends(get_preco_service)):
    service.deletar(preco_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
