"""Token de acesso assinado (HMAC-SHA256), sem dependências externas.

Formato: base64url("<usuario_id>.<expira_em>") + "." + assinatura
"""
import base64
import hashlib
import hmac
import time

from app.core.config import get_settings


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).decode().rstrip("=")


def _unb64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def _assinar(carga: str) -> str:
    chave = get_settings().secret_key.encode()
    return _b64(hmac.new(chave, carga.encode(), hashlib.sha256).digest())


def criar_token(usuario_id: int) -> tuple[str, int]:
    """Retorna (token, segundos até expirar)."""
    duracao = get_settings().token_horas * 3600
    carga = _b64(f"{usuario_id}.{int(time.time()) + duracao}".encode())
    return f"{carga}.{_assinar(carga)}", duracao


def ler_token(token: str) -> int | None:
    """Devolve o id do usuário se o token for válido e não estiver expirado; senão None."""
    try:
        carga, assinatura = token.split(".")
        if not hmac.compare_digest(assinatura, _assinar(carga)):
            return None
        usuario_id, expira = _unb64(carga).decode().split(".")
        if int(expira) < time.time():
            return None
        return int(usuario_id)
    except (ValueError, UnicodeDecodeError):
        return None
