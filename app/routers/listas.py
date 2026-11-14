from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.dependencies import get_lista_service, get_usuario_atual
from app.schemas.erro import respostas
from app.schemas.lista import (
    ComparacaoListaOut,
    ItemCreate,
    ItemOut,
    ItemUpdate,
    ListaCreate,
    ListaOut,
    ListaResumoOut,
    ListaUpdate,
)
from app.services.lista_service import ListaService

router = APIRouter(prefix="/listas", tags=["Listas de compras"])

ListaId = Path(gt=0, description="ID da lista.", examples=[1])
ItemId = Path(gt=0, description="ID do item na lista.", examples=[1])
_ERROS = {
    **respostas(404, 422),
    401: {"description": "Token ausente, inválido ou expirado."},
    403: {"description": "A lista pertence a outro usuário."},
}


@router.get("", response_model=list[ListaResumoOut], summary="Minhas listas", responses=_ERROS)
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usuario=Depends(get_usuario_atual),
    service: ListaService = Depends(get_lista_service),
):
    return service.listar_do_usuario(usuario.id, limit, offset)


@router.post("", response_model=ListaOut, status_code=status.HTTP_201_CREATED, summary="Criar lista", responses=_ERROS)
def criar(payload: ListaCreate, usuario=Depends(get_usuario_atual), service: ListaService = Depends(get_lista_service)):
    lista = service.criar_para(usuario.id, payload.model_dump())
    return {**vars(lista), "itens": []}


@router.get("/{lista_id}", response_model=ListaOut, summary="Lista com itens", responses=_ERROS)
def obter(
    lista_id: int = ListaId, usuario=Depends(get_usuario_atual), service: ListaService = Depends(get_lista_service)
):
    return service.detalhar(lista_id, usuario.id)


@router.patch(
    "/{lista_id}", response_model=ListaResumoOut, summary="Renomear lista", responses={**_ERROS, **respostas(400)}
)
def renomear(
    payload: ListaUpdate,
    lista_id: int = ListaId,
    usuario=Depends(get_usuario_atual),
    service: ListaService = Depends(get_lista_service),
):
    service.renomear(lista_id, usuario.id, payload.model_dump(exclude_unset=True))
    return next(x for x in service.listar_do_usuario(usuario.id, 200, 0) if x["id"] == lista_id)


@router.delete(
    "/{lista_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Excluir lista",
    responses=_ERROS,
)
def excluir(
    lista_id: int = ListaId, usuario=Depends(get_usuario_atual), service: ListaService = Depends(get_lista_service)
):
    service.excluir(lista_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{lista_id}/itens",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar item",
    responses={**_ERROS, **respostas(409)},
)
def adicionar_item(
    payload: ItemCreate,
    lista_id: int = ListaId,
    usuario=Depends(get_usuario_atual),
    service: ListaService = Depends(get_lista_service),
):
    """Produto que já está na lista retorna 409 (altere a quantidade com PATCH)."""
    return service.adicionar_item(lista_id, usuario.id, payload.model_dump())


@router.patch(
    "/{lista_id}/itens/{item_id}",
    response_model=ItemOut,
    summary="Alterar quantidade / marcar como comprado",
    responses={**_ERROS, **respostas(400)},
)
def alterar_item(
    payload: ItemUpdate,
    lista_id: int = ListaId,
    item_id: int = ItemId,
    usuario=Depends(get_usuario_atual),
    service: ListaService = Depends(get_lista_service),
):
    return service.alterar_item(lista_id, item_id, usuario.id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{lista_id}/itens/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remover item",
    responses=_ERROS,
)
def remover_item(
    lista_id: int = ListaId,
    item_id: int = ItemId,
    usuario=Depends(get_usuario_atual),
    service: ListaService = Depends(get_lista_service),
):
    service.remover_item(lista_id, item_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{lista_id}/comparacao",
    response_model=ComparacaoListaOut,
    summary="Em qual supermercado a lista sai mais barata",
    responses=_ERROS,
)
def comparar(
    lista_id: int = ListaId, usuario=Depends(get_usuario_atual), service: ListaService = Depends(get_lista_service)
):
    return service.comparar(lista_id, usuario.id)
