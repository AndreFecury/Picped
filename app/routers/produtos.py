from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.dependencies import get_preco_service, get_produto_service
from app.schemas.erro import respostas
from app.schemas.preco import ComparacaoOut
from app.schemas.produto import ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.services.preco_service import PrecoService
from app.services.produto_service import ProdutoService

router = APIRouter(prefix="/produtos", tags=["Produtos"])

ProdutoId = Path(gt=0, description="ID do produto.", examples=[1])


@router.get("", response_model=list[ProdutoOut], summary="Listar produtos", responses=respostas(422))
def listar(
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: ProdutoService = Depends(get_produto_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=ProdutoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    responses=respostas(400, 409, 422),
)
def criar(payload: ProdutoCreate, service: ProdutoService = Depends(get_produto_service)):
    """Regra de negócio: a categoria informada precisa existir (senão 422)."""
    return service.criar(payload.model_dump())


@router.get("/{produto_id}", response_model=ProdutoOut, summary="Buscar produto", responses=respostas(404, 422))
def obter(produto_id: int = ProdutoId, service: ProdutoService = Depends(get_produto_service)):
    return service.obter(produto_id)


@router.get(
    "/{produto_id}/comparacao",
    response_model=ComparacaoOut,
    summary="Comparar preços do produto entre supermercados",
    responses=respostas(404, 422),
)
def comparar_precos(produto_id: int = ProdutoId, service: PrecoService = Depends(get_preco_service)):
    """Preço atual do produto em cada supermercado, do mais barato ao mais caro, com a economia possível."""
    return service.comparar(produto_id)


@router.patch(
    "/{produto_id}",
    response_model=ProdutoOut,
    summary="Atualizar produto (parcial)",
    responses=respostas(400, 404, 409, 422),
)
def atualizar(
    payload: ProdutoUpdate,
    produto_id: int = ProdutoId,
    service: ProdutoService = Depends(get_produto_service),
):
    return service.atualizar(produto_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto",
    response_class=Response,
    responses=respostas(404, 409, 422),
)
def deletar(produto_id: int = ProdutoId, service: ProdutoService = Depends(get_produto_service)):
    """Retorna 409 se o produto tiver preços ou itens de lista vinculados."""
    service.deletar(produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
