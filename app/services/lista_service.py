from decimal import Decimal

from app.core.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.repositories.lista_repository import ItemListaRepository, ListaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.services.base import BaseService, normalizar_texto


class ListaService(BaseService):
    """Listas de compras: cada usuário só enxerga e altera as próprias listas."""

    entidade = "Lista"

    def __init__(self, repo: ListaRepository, itens: ItemListaRepository, produtos: ProdutoRepository) -> None:
        super().__init__(repo)
        self.itens = itens
        self.produtos = produtos

    # ---------- listas ----------
    def obter_do_usuario(self, lista_id: int, usuario_id: int):
        lista = self.obter(lista_id)  # 404 se não existir
        if lista.usuario_id != usuario_id:
            raise ForbiddenError("Esta lista pertence a outro usuário.")
        return lista

    def listar_do_usuario(self, usuario_id: int, limit: int, offset: int):
        return self.repo.listar_do_usuario(usuario_id, limit, offset)

    def detalhar(self, lista_id: int, usuario_id: int) -> dict:
        lista = self.obter_do_usuario(lista_id, usuario_id)
        return {**vars(lista), "itens": self.repo.itens_detalhados(lista_id)}

    def criar_para(self, usuario_id: int, dados: dict):
        dados["nome"] = normalizar_texto(dados["nome"])
        return self.repo.criar({**dados, "usuario_id": usuario_id})

    def renomear(self, lista_id: int, usuario_id: int, dados: dict):
        self.obter_do_usuario(lista_id, usuario_id)
        self.exigir_campos(dados)
        dados["nome"] = normalizar_texto(dados["nome"])
        return self.repo.atualizar(lista_id, dados)

    def excluir(self, lista_id: int, usuario_id: int) -> None:
        self.obter_do_usuario(lista_id, usuario_id)
        self.repo.deletar(lista_id)  # itens apagados em cascata (ON DELETE CASCADE)

    # ---------- itens ----------
    def adicionar_item(self, lista_id: int, usuario_id: int, dados: dict):
        self.obter_do_usuario(lista_id, usuario_id)
        if not self.produtos.existe(dados["produto_id"]):
            raise BusinessRuleError(f"O produto {dados['produto_id']} não existe.")
        return self.itens.criar({**dados, "lista_id": lista_id})  # produto repetido -> 409 (UNIQUE)

    def _item(self, lista_id: int, item_id: int, usuario_id: int):
        self.obter_do_usuario(lista_id, usuario_id)
        item = self.itens.buscar_na_lista(lista_id, item_id)
        if item is None:
            raise NotFoundError(f"Item {item_id} não encontrado nesta lista.")
        return item

    def alterar_item(self, lista_id: int, item_id: int, usuario_id: int, dados: dict):
        self._item(lista_id, item_id, usuario_id)
        self.exigir_campos(dados)
        return self.itens.atualizar(item_id, dados)

    def remover_item(self, lista_id: int, item_id: int, usuario_id: int) -> None:
        self._item(lista_id, item_id, usuario_id)
        self.itens.deletar(item_id)

    # ---------- regra principal: onde a lista sai mais barata ----------
    def comparar(self, lista_id: int, usuario_id: int) -> dict:
        lista = self.obter_do_usuario(lista_id, usuario_id)
        total_itens = len(self.repo.itens_detalhados(lista_id))

        mercados: dict[int, dict] = {}
        for linha in self.repo.precos_dos_itens(lista_id):
            m = mercados.setdefault(
                linha["supermercado_id"],
                {
                    "supermercado_id": linha["supermercado_id"],
                    "supermercado_nome": linha["supermercado_nome"],
                    "total": Decimal("0"),
                    "itens_encontrados": 0,
                },
            )
            m["total"] += (linha["valor"] * linha["quantidade"]).quantize(Decimal("0.01"))
            m["itens_encontrados"] += 1

        for m in mercados.values():
            m["itens_faltando"] = total_itens - m["itens_encontrados"]
            m["completo"] = m["itens_faltando"] == 0

        # quem tem todos os itens vem primeiro (do mais barato ao mais caro); os parciais depois,
        # dos que têm mais itens para os que têm menos — total parcial não é comparável com total completo
        ranking = sorted(mercados.values(), key=lambda m: (m["itens_faltando"], m["total"]))
        completos = [m for m in ranking if m["completo"]]
        economia = completos[-1]["total"] - completos[0]["total"] if len(completos) >= 2 else Decimal("0")
        percentual = (
            (economia / completos[-1]["total"] * 100).quantize(Decimal("0.01"))
            if len(completos) >= 2 and completos[-1]["total"] > 0
            else Decimal("0")
        )
        return {
            "referencia": (
                "Preço mais recente registrado de cada item em cada supermercado ativo × quantidade. "
                "Economia = total do mercado completo mais caro − total do mais barato (economia potencial)."
            ),
            "economia_percentual": percentual,
            "lista_id": lista.id,
            "lista_nome": lista.nome,
            "total_itens": total_itens,
            "melhor_opcao": completos[0] if completos else None,
            "economia": economia,
            "supermercados": ranking,
        }
