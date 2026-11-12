from app.core.exceptions import UnauthorizedError
from app.core.security import criar_token, ler_token
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuario_service import verificar_senha


class AuthService:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self.usuarios = usuarios

    def login(self, email: str, senha: str) -> dict:
        usuario = self.usuarios.buscar_por_email(email)
        # mesma mensagem para e-mail inexistente e senha errada (não revela quais e-mails existem)
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise UnauthorizedError("E-mail ou senha incorretos.")
        token, expira_em = criar_token(usuario.id)
        return {"access_token": token, "token_type": "bearer", "expira_em": expira_em, "usuario": usuario}

    def usuario_do_token(self, token: str | None):
        if not token:
            raise UnauthorizedError("Faça login para continuar (envie Authorization: Bearer <token>).")
        usuario_id = ler_token(token)
        usuario = self.usuarios.buscar_por_id(usuario_id) if usuario_id else None
        if usuario is None:
            raise UnauthorizedError("Sessão inválida ou expirada. Faça login novamente.")
        return usuario
