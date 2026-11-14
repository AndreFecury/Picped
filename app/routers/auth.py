from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_auth_service, get_usuario_atual, get_usuario_service
from app.schemas.auth import LoginIn, TokenOut
from app.schemas.erro import respostas
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticação"])

_401 = {401: {"description": "Token ausente, inválido ou expirado."}}


@router.post(
    "/login", response_model=TokenOut, summary="Entrar (gera o token)", responses={**respostas(400, 422), **_401}
)
def login(payload: LoginIn, auth: AuthService = Depends(get_auth_service)):
    """Use o `access_token` no botão **Authorize** do Swagger ou no cabeçalho `Authorization: Bearer <token>`."""
    return auth.login(payload.email, payload.senha)


@router.get("/me", response_model=UsuarioOut, summary="Usuário logado", responses=_401)
def eu(usuario=Depends(get_usuario_atual)):
    return usuario


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Excluir minha conta (LGPD)",
    responses=_401,
)
def excluir_conta(usuario=Depends(get_usuario_atual), service: UsuarioService = Depends(get_usuario_service)):
    """Apaga o usuário, suas listas e os preços que ele registrou."""
    service.excluir_conta(usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
