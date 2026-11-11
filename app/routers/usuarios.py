from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import get_usuario_service
from app.schemas.base import IdPath
from app.schemas.erro import respostas
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuários"], responses=respostas(422))


@router.get("", response_model=list[UsuarioOut], summary="Listar usuários")
def listar(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.listar(limit, offset)


@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    description="O e-mail é único (409 se já existir). A senha é gravada só como hash PBKDF2.",
    responses=respostas(400, 409),
)
def criar(payload: UsuarioCreate, service: UsuarioService = Depends(get_usuario_service)):
    return service.criar(payload.model_dump())


@router.get("/{usuario_id}", response_model=UsuarioOut, summary="Obter usuário", responses=respostas(404))
def obter(usuario_id: IdPath, service: UsuarioService = Depends(get_usuario_service)):
    return service.obter(usuario_id)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Substituir usuário",
    responses=respostas(400, 404, 409),
)
def substituir(usuario_id: IdPath, payload: UsuarioCreate, service: UsuarioService = Depends(get_usuario_service)):
    return service.substituir(usuario_id, payload.model_dump())


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Atualizar parte do usuário",
    responses=respostas(400, 404, 409),
)
def atualizar(usuario_id: IdPath, payload: UsuarioUpdate, service: UsuarioService = Depends(get_usuario_service)):
    return service.atualizar(usuario_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir usuário",
    description="Retorna 409 se o usuário tiver preços registrados.",
    responses=respostas(404, 409),
)
def deletar(usuario_id: IdPath, service: UsuarioService = Depends(get_usuario_service)):
    service.deletar(usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
