import hashlib
import hmac
import secrets

from app.repositories.usuario_repository import UsuarioRepository
from app.services.base import BaseService, normalizar_texto

_ITERACOES = 600_000


def gerar_hash_senha(senha: str) -> str:
    """PBKDF2-SHA256 com salt aleatório (biblioteca padrão). Formato: pbkdf2_sha256$iter$salt$hash."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERACOES).hex()
    return f"pbkdf2_sha256${_ITERACOES}${salt}${digest}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        algoritmo, iteracoes, salt, digest = senha_hash.split("$")
    except ValueError:
        return False
    if algoritmo != "pbkdf2_sha256":
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), int(iteracoes)).hex()
    return hmac.compare_digest(calculado, digest)


class UsuarioService(BaseService):
    entidade = "Usuário"

    def __init__(self, repo: UsuarioRepository) -> None:
        super().__init__(repo)

    @staticmethod
    def _preparar(dados: dict) -> None:
        """Normaliza nome/e-mail e troca a senha em texto pelo hash (a senha nunca vai para o banco)."""
        if dados.get("nome"):
            dados["nome"] = normalizar_texto(dados["nome"])
        if dados.get("email"):
            dados["email"] = dados["email"].lower()
        if "senha" in dados:
            dados["senha_hash"] = gerar_hash_senha(dados.pop("senha"))

    def criar(self, dados):
        self._preparar(dados)
        return super().criar(dados)

    def atualizar(self, id_, dados):
        self.obter(id_)
        self.exigir_campos(dados)
        self._preparar(dados)
        return self.repo.atualizar(id_, dados)

    def excluir_conta(self, id_: int) -> None:
        """Direito de exclusão (LGPD): remove os preços do usuário e depois a conta (listas caem em cascata)."""
        self.obter(id_)
        self.repo.excluir_com_dados(id_)
