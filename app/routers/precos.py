from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.core.exceptions import ForbiddenError
from app.dependencies import get_preco_service, get_usuario_opcional
from app.schemas.erro import respostas
from app.schemas.preco import PrecoCreate, PrecoOut, PrecoUpdate
from app.services.preco_service import PrecoService

router = APIRouter(prefix="/precos", tags=["Preços"])

PrecoId = Path(gt=0, description="ID do registro de preço.", examples=[1])


@router.get("", response_model=list[PrecoOut], summary="Listar preços", responses=respostas(422))
def listar(
    produto_id: Optional[int] = Query(None, gt=0, description="Filtra por produto."),
    supermercado_id: Optional[int] = Query(None, gt=0, description="Filtra por supermercado."),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: PrecoService = Depends(get_preco_service),
):
    return service.listar(limit, offset, produto_id, supermercado_id)


@router.post(
    "",
    response_model=PrecoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar preço",
    responses=respostas(400, 422),
)
def criar(
    payload: PrecoCreate,
    usuario=Depends(get_usuario_opcional),
    service: PrecoService = Depends(get_preco_service),
):
    """
    Com token (app), o `usuario_id` precisa ser o do próprio usuário logado (senão 403).

    Regras de negócio (422 se violadas): produto, supermercado e usuário precisam existir,
    o supermercado precisa estar ativo e `distancia_metros` não pode passar do raio do mercado.
    """
    if usuario is not None and usuario.id != payload.usuario_id:
        raise ForbiddenError("Você só pode registrar preços em seu próprio nome.")
    return service.criar(payload.model_dump())


@router.get("/{preco_id}", response_model=PrecoOut, summary="Buscar preço", responses=respostas(404, 422))
def obter(preco_id: int = PrecoId, service: PrecoService = Depends(get_preco_service)):
    return service.obter(preco_id)


@router.patch(
    "/{preco_id}",
    response_model=PrecoOut,
    summary="Corrigir valor do preço",
    responses=respostas(400, 404, 422),
)
def atualizar(
    payload: PrecoUpdate,
    preco_id: int = PrecoId,
    service: PrecoService = Depends(get_preco_service),
):
    return service.atualizar(preco_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{preco_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir preço",
    response_class=Response,
    responses=respostas(404, 422),
)
def deletar(preco_id: int = PrecoId, service: PrecoService = Depends(get_preco_service)):
    service.deletar(preco_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
