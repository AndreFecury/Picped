from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.dependencies import get_usuario_service
from app.schemas.erro import respostas
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

UsuarioId = Path(gt=0, description="ID do usuário.", examples=[1])


@router.get("", response_model=list[UsuarioOut], summary="Listar usuários", responses=respostas(422))
def listar(
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros."),
    offset: int = Query(0, ge=0, description="Quantos registros pular (paginação)."),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    responses=respostas(400, 409, 422),
)
def criar(payload: UsuarioCreate, service: UsuarioService = Depends(get_usuario_service)):
    """A senha é guardada só como hash; e-mail duplicado retorna 409."""
    return service.criar(payload.model_dump())


@router.get("/{usuario_id}", response_model=UsuarioOut, summary="Buscar usuário", responses=respostas(404, 422))
def obter(usuario_id: int = UsuarioId, service: UsuarioService = Depends(get_usuario_service)):
    return service.obter(usuario_id)


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Atualizar usuário (parcial)",
    responses=respostas(400, 404, 409, 422),
)
def atualizar(
    payload: UsuarioUpdate,
    usuario_id: int = UsuarioId,
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.atualizar(usuario_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir usuário",
    response_class=Response,
    responses=respostas(404, 409, 422),
)
def deletar(usuario_id: int = UsuarioId, service: UsuarioService = Depends(get_usuario_service)):
    """Retorna 409 se o usuário já registrou preços (as listas de compras são apagadas junto)."""
    service.deletar(usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
