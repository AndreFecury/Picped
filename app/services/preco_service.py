from decimal import Decimal
from typing import Optional

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.repositories.preco_repository import PrecoRepository
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.supermercado_repository import SupermercadoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.base import BaseService


class PrecoService(BaseService):
    entidade = "Preço"

    def __init__(
        self,
        repo: PrecoRepository,
        produtos: ProdutoRepository,
        supermercados: SupermercadoRepository,
        usuarios: UsuarioRepository,
    ) -> None:
        super().__init__(repo)
        self.produtos = produtos
        self.supermercados = supermercados
        self.usuarios = usuarios

    def listar(
        self,
        limit: int = 50,
        offset: int = 0,
        produto_id: Optional[int] = None,
        supermercado_id: Optional[int] = None,
    ):
        return self.repo.listar(limit, offset, produto_id, supermercado_id)

    def criar(self, dados):
        """Regras: referências existem, mercado ativo e usuário dentro do raio do mercado."""
        if not self.produtos.existe(dados["produto_id"]):
            raise BusinessRuleError(f"O produto {dados['produto_id']} não existe.")
        if not self.usuarios.existe(dados["usuario_id"]):
            raise BusinessRuleError(f"O usuário {dados['usuario_id']} não existe.")

        mercado = self.supermercados.buscar_por_id(dados["supermercado_id"])
        if mercado is None:
            raise BusinessRuleError(f"O supermercado {dados['supermercado_id']} não existe.")
        if not mercado.ativo:
            raise BusinessRuleError("Este supermercado está inativo e não aceita novos preços.")

        distancia = dados.get("distancia_metros")
        if distancia is not None and distancia > mercado.raio_metros:
            raise BusinessRuleError(
                f"Registro rejeitado: o usuário está a {distancia} m do supermercado "
                f"(máximo permitido: {mercado.raio_metros} m)."
            )
        return super().criar(dados)

    def comparar(self, produto_id: int) -> dict:
        """Compara o preço atual do produto entre os supermercados e calcula a economia possível."""
        produto = self.produtos.buscar_por_id(produto_id)
        if produto is None:
            raise NotFoundError(f"Produto {produto_id} não encontrado(a).")

        ofertas = sorted(self.repo.ultimos_por_supermercado(produto_id), key=lambda o: o["valor"])
        economia = Decimal("0")
        percentual = Decimal("0")
        if len(ofertas) >= 2:
            maior, menor = ofertas[-1]["valor"], ofertas[0]["valor"]
            economia = maior - menor
            percentual = (economia / maior * 100).quantize(Decimal("0.01"))

        return {
            "produto_id": produto.id,
            "produto_nome": produto.nome,
            "menor_preco": ofertas[0] if ofertas else None,
            "maior_preco": ofertas[-1] if ofertas else None,
            "economia": economia,
            "economia_percentual": percentual,
            "ofertas": ofertas,
        }
