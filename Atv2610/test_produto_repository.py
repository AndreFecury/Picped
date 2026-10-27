import unittest

from produto_repository import ProdutoError, ProdutoRepository


class TestProdutoRepository(unittest.TestCase):
    def setUp(self):
        self.repo = ProdutoRepository()
        # categoria existente (criada pelo seed.sql)
        self.categoria_id = self.repo._consultar("SELECT id FROM categoria ORDER BY id")["id"]
        self.criados = []

    def tearDown(self):
        # limpa o que o teste criou, mesmo se ele falhar
        for produto_id in self.criados:
            self.repo.deletar(produto_id)

    def _novo(self, nome="Produto Teste CRUD", **extra):
        produto = self.repo.criar(
            nome=nome, unidade_medida="un", categoria_id=self.categoria_id,
            marca="Marca Teste", **extra,
        )
        self.criados.append(produto["id"])
        return produto

    # ---------------- CREATE ----------------
    def test_criar_devolve_registro_com_id(self):
        produto = self._novo()
        self.assertIsNotNone(produto["id"])
        self.assertEqual(produto["nome"], "Produto Teste CRUD")
        self.assertEqual(produto["unidade_medida"], "un")

    def test_criar_com_unidade_invalida_falha(self):
        with self.assertRaises(ProdutoError):
            self.repo.criar("Produto Inválido", "caixa", self.categoria_id)

    def test_criar_com_categoria_inexistente_falha(self):
        with self.assertRaises(ProdutoError):
            self.repo.criar("Produto Órfão", "un", 999999)

    def test_criar_duplicado_falha(self):
        self._novo()
        with self.assertRaises(ProdutoError):
            self._novo()

    # ---------------- READ ----------------
    def test_buscar_por_id_existente(self):
        criado = self._novo()
        encontrado = self.repo.buscar_por_id(criado["id"])
        self.assertEqual(encontrado, criado)

    def test_buscar_por_id_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.buscar_por_id(999999))

    def test_listar_contem_produto_criado_e_respeita_limite(self):
        criado = self._novo()
        todos = self.repo.listar(limite=1000)
        self.assertIn(criado["id"], [p["id"] for p in todos])
        self.assertEqual(len(self.repo.listar(limite=3)), 3)

    # ---------------- UPDATE ----------------
    def test_atualizar_altera_somente_campos_informados(self):
        criado = self._novo()
        atualizado = self.repo.atualizar(criado["id"], nome="Produto Teste Editado", marca="Outra Marca")
        self.assertEqual(atualizado["nome"], "Produto Teste Editado")
        self.assertEqual(atualizado["marca"], "Outra Marca")
        self.assertEqual(atualizado["unidade_medida"], criado["unidade_medida"])

    def test_atualizar_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.atualizar(999999, nome="Qualquer"))

    def test_atualizar_campo_proibido_levanta_erro(self):
        criado = self._novo()
        with self.assertRaises(ValueError):
            self.repo.atualizar(criado["id"], id=1)

    def test_atualizar_sem_campos_levanta_erro(self):
        criado = self._novo()
        with self.assertRaises(ValueError):
            self.repo.atualizar(criado["id"])

    # ---------------- DELETE ----------------
    def test_deletar_remove_o_produto(self):
        criado = self._novo()
        self.assertTrue(self.repo.deletar(criado["id"]))
        self.assertIsNone(self.repo.buscar_por_id(criado["id"]))

    def test_deletar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.deletar(999999))

    def test_deletar_produto_com_precos_e_bloqueado(self):
        # o seed.sql registra preços para vários produtos
        em_uso = self.repo._consultar("SELECT produto_id FROM preco LIMIT 1")["produto_id"]
        with self.assertRaises(ProdutoError):
            self.repo.deletar(em_uso)


if __name__ == "__main__":
    unittest.main(verbosity=2)
