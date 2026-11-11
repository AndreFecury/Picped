from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_preco_service
from app.schemas.base import IdPath
from app.schemas.erro import respostas
from app.schemas.preco import PrecoCreate, PrecoOut, PrecoUpdate
from app.services.preco_service import PrecoService

router = APIRouter(prefix="/precos", tags=["Preços"], responses=respostas(422))

_REGRAS = (
    "Regras de negócio (422): produto, supermercado e usuário precisam existir; "
    "o supermercado precisa estar ativo; `distancia_metros` não pode passar do raio do supermercado."
)


@router.get("", response_model=list[PrecoOut], summary="Listar preços (mais recentes primeiro)")
def listar(
    produto_id: Optional[int] = Query(None, gt=0),
    supermercado_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: PrecoService = Depends(get_preco_service),
):
    return service.listar(limit, offset, produto_id, supermercado_id)


@router.post(
    "",
    response_model=PrecoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar preço",
    description=_REGRAS,
    responses=respostas(400),
)
def criar(payload: PrecoCreate, service: PrecoService = Depends(get_preco_service)):
    return service.criar(payload.model_dump())


@router.get("/{preco_id}", response_model=PrecoOut, summary="Obter preço", responses=respostas(404))
def obter(preco_id: IdPath, service: PrecoService = Depends(get_preco_service)):
    return service.obter(preco_id)


@router.put(
    "/{preco_id}",
    response_model=PrecoOut,
    summary="Substituir preço",
    description=_REGRAS,
    responses=respostas(400, 404),
)
def substituir(preco_id: IdPath, payload: PrecoCreate, service: PrecoService = Depends(get_preco_service)):
    return service.substituir(preco_id, payload.model_dump())


@router.patch(
    "/{preco_id}",
    response_model=PrecoOut,
    summary="Corrigir o valor do preço",
    responses=respostas(400, 404),
)
def atualizar(preco_id: IdPath, payload: PrecoUpdate, service: PrecoService = Depends(get_preco_service)):
    return service.atualizar(preco_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{preco_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir preço", responses=respostas(404)
)
def deletar(preco_id: IdPath, service: PrecoService = Depends(get_preco_service)):
    service.deletar(preco_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
