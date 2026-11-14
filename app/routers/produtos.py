from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_preco_service, get_produto_service
from app.schemas.base import IdPath
from app.schemas.erro import respostas
from app.schemas.preco import ComparacaoOut, HistoricoOut
from app.schemas.produto import ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.services.preco_service import PrecoService
from app.services.produto_service import ProdutoService

router = APIRouter(prefix="/produtos", tags=["Produtos"], responses=respostas(422))


@router.get("", response_model=list[ProdutoOut], summary="Listar produtos")
def listar(
    busca: Optional[str] = Query(None, min_length=2, max_length=60, description="Parte do nome ou da marca."),
    codigo_barras: Optional[str] = Query(None, pattern=r"^[0-9]{8,14}$", description="EAN lido pela câmera."),
    categoria_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: ProdutoService = Depends(get_produto_service),
):
    return service.listar(limit, offset, busca, codigo_barras, categoria_id)


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


@router.get(
    "/{produto_id}/historico",
    response_model=HistoricoOut,
    summary="Histórico de preços do produto",
    responses=respostas(404, 422),
)
def historico(produto_id: IdPath, service: PrecoService = Depends(get_preco_service)):
    """Mínimo, máximo, média e variação calculados apenas com os registros existentes."""
    return service.historico(produto_id)


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
