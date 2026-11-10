from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_preco_service, get_produto_service
from app.schemas.preco import ComparacaoOut
from app.schemas.produto import ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.services.preco_service import PrecoService
from app.services.produto_service import ProdutoService

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoOut])
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ProdutoService = Depends(get_produto_service),
):
    return service.listar(limit, offset)


@router.post("", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar(payload: ProdutoCreate, service: ProdutoService = Depends(get_produto_service)):
    return service.criar(payload.model_dump())


@router.get("/{produto_id}", response_model=ProdutoOut)
def obter(produto_id: int, service: ProdutoService = Depends(get_produto_service)):
    return service.obter(produto_id)


@router.get("/{produto_id}/comparacao", response_model=ComparacaoOut)
def comparar_precos(produto_id: int, service: PrecoService = Depends(get_preco_service)):
    """Preço atual do produto em cada supermercado, do mais barato ao mais caro, com a economia possível."""
    return service.comparar(produto_id)


@router.patch("/{produto_id}", response_model=ProdutoOut)
def atualizar(
    produto_id: int,
    payload: ProdutoUpdate,
    service: ProdutoService = Depends(get_produto_service),
):
    return service.atualizar(produto_id, payload.model_dump(exclude_unset=True))


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(produto_id: int, service: ProdutoService = Depends(get_produto_service)):
    service.deletar(produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
