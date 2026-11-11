from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_preco_service, get_produto_service
from app.schemas.base import IdPath
from app.schemas.erro import respostas
from app.schemas.preco import ComparacaoOut
from app.schemas.produto import ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.services.preco_service import PrecoService
from app.services.produto_service import ProdutoService

router = APIRouter(prefix="/produtos", tags=["Produtos"], responses=respostas(422))


@router.get("", response_model=list[ProdutoOut], summary="Listar produtos")
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ProdutoService = Depends(get_produto_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=ProdutoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    description="A categoria informada precisa existir (senão 422).",
    responses=respostas(400, 409),
)
def criar(payload: ProdutoCreate, service: ProdutoService = Depends(get_produto_service)):
    return service.criar(payload.model_dump())


@router.get("/{produto_id}", response_model=ProdutoOut, summary="Obter produto", responses=respostas(404))
def obter(produto_id: IdPath, service: ProdutoService = Depends(get_produto_service)):
    return service.obter(produto_id)


@router.get(
    "/{produto_id}/comparacao",
    response_model=ComparacaoOut,
    summary="Comparar preços do produto",
    responses=respostas(404),
)
def comparar_precos(produto_id: IdPath, service: PrecoService = Depends(get_preco_service)):
    """Preço atual do produto em cada supermercado, do mais barato ao mais caro, com a economia possível."""
    return service.comparar(produto_id)


@router.put(
    "/{produto_id}",
    response_model=ProdutoOut,
    summary="Substituir produto",
    responses=respostas(400, 404, 409),
)
def substituir(
    produto_id: IdPath,
    payload: ProdutoCreate,
    service: ProdutoService = Depends(get_produto_service),
):
    return service.substituir(produto_id, payload.model_dump())


@router.patch(
    "/{produto_id}",
    response_model=ProdutoOut,
    summary="Atualizar parte do produto",
    responses=respostas(400, 404, 409),
)
def atualizar(
    produto_id: IdPath,
    payload: ProdutoUpdate,
    service: ProdutoService = Depends(get_produto_service),
):
    return service.atualizar(produto_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto",
    description="Retorna 409 se o produto tiver preços registrados.",
    responses=respostas(404, 409),
)
def deletar(produto_id: IdPath, service: ProdutoService = Depends(get_produto_service)):
    service.deletar(produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
