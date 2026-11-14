import hashlib
import hmac
import secrets

from app.core.exceptions import ConflictError
from app.repositories.usuario_repository import UsuarioRepository
from app.services.base import BaseService, normalizar_texto

_ITERACOES = 210_000  # PBKDF2-SHA256 (recomendação OWASP)


def gerar_hash_senha(senha: str) -> str:
    """Formato: pbkdf2_sha256$iteracoes$salt$hash (o salt é aleatório por usuário)."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERACOES).hex()
    return f"pbkdf2_sha256${_ITERACOES}${salt}${digest}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        _, iteracoes, salt, digest = senha_hash.split("$")
    except ValueError:
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), int(iteracoes)).hex()
    return hmac.compare_digest(calculado, digest)


class UsuarioService(BaseService):
    entidade = "Usuário"

    def __init__(self, repo: UsuarioRepository) -> None:
        super().__init__(repo)

    def _preparar(self, dados: dict, id_atual: int | None = None) -> dict:
        """Regras: e-mail único (sem diferenciar maiúsculas) e senha nunca gravada em texto."""
        if dados.get("nome"):
            dados["nome"] = normalizar_texto(dados["nome"])
        if dados.get("email"):
            dados["email"] = dados["email"].lower()
            dono = self.repo.buscar_por_email(dados["email"])
            if dono is not None and dono.id != id_atual:
                raise ConflictError(f"O e-mail {dados['email']} já está cadastrado.")
        if "senha" in dados:
            dados["senha_hash"] = gerar_hash_senha(dados.pop("senha"))
        return dados

    def criar(self, dados):
        return super().criar(self._preparar(dados))

    def substituir(self, id_, dados):
        self.obter(id_)
        return super().substituir(id_, self._preparar(dados, id_))

    def atualizar(self, id_, dados):
        if dados:
            self.obter(id_)
        return super().atualizar(id_, self._preparar(dados, id_))

    def excluir_conta(self, id_: int) -> None:
        """Direito de exclusão (LGPD): remove os preços do usuário e depois a conta (listas caem em cascata)."""
        self.obter(id_)
        self.repo.excluir_com_dados(id_)
