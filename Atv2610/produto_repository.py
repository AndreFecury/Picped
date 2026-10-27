import os

import psycopg
from psycopg import errors
from psycopg.rows import dict_row


class ProdutoError(Exception):
    """Erro de regra de negócio ou de integridade ao operar produtos."""


class ProdutoRepository:
    COLUNAS = "id, nome, marca, unidade_medida, codigo_barras, categoria_id"
    CAMPOS_ATUALIZAVEIS = (
        "nome", "marca", "unidade_medida", "codigo_barras", "categoria_id",
    )

    def __init__(self, host=None, port=None, dbname=None, user=None, password=None):
        # Valores padrão batem com o container Docker (picped-db).
        self._params = {
            "host": host or os.getenv("PGHOST", "localhost"),
            "port": int(port or os.getenv("PGPORT", "5432")),
            "dbname": dbname or os.getenv("PGDATABASE", "picped"),
            "user": user or os.getenv("PGUSER", "postgres"),
            "password": password or os.getenv("PGPASSWORD", "picped"),
        }

    # ------------------------------------------------------------------
    # Infraestrutura
    # ------------------------------------------------------------------
    def _conectar(self):
        return psycopg.connect(**self._params, row_factory=dict_row)

    def _consultar(self, sql, params=(), todos=False):
        with self._conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall() if todos else cur.fetchone()

    def _escrever(self, sql, params=()):
        """Executa INSERT/UPDATE/DELETE e traduz erros do banco."""
        try:
            with self._conectar() as conn:  # commit automático ao sair do with
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    linha = cur.fetchone() if cur.description else None
                    return linha, cur.rowcount
        except errors.UniqueViolation as erro:
            raise ProdutoError(
                "Já existe um produto com esse nome/marca ou código de barras."
            ) from erro
        except errors.ForeignKeyViolation as erro:
            raise ProdutoError(
                "Operação bloqueada por relacionamento: categoria inexistente "
                "ou produto com preços/itens de lista vinculados."
            ) from erro
        except (errors.CheckViolation, errors.NotNullViolation) as erro:
            raise ProdutoError(
                "Dados inválidos: confira unidade de medida, código de barras e campos obrigatórios."
            ) from erro

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def criar(self, nome, unidade_medida, categoria_id, marca=None, codigo_barras=None):
        """CREATE: insere um produto e devolve o registro criado (dict)."""
        sql = (
            "INSERT INTO produto (nome, marca, unidade_medida, codigo_barras, categoria_id) "
            f"VALUES (%s, %s, %s, %s, %s) RETURNING {self.COLUNAS}"
        )
        linha, _ = self._escrever(
            sql, (nome, marca, unidade_medida, codigo_barras, categoria_id)
        )
        return linha

    def buscar_por_id(self, produto_id):
        """READ: devolve o produto (dict) ou None se não existir."""
        sql = f"SELECT {self.COLUNAS} FROM produto WHERE id = %s"
        return self._consultar(sql, (produto_id,))

    def listar(self, limite=50, offset=0):
        """READ: devolve uma lista de produtos ordenada por id."""
        sql = (
            f"SELECT {self.COLUNAS} FROM produto ORDER BY id LIMIT %s OFFSET %s"
        )
        return self._consultar(sql, (limite, offset), todos=True)

    def atualizar(self, produto_id, **campos):
        """UPDATE: altera só os campos informados. Devolve o registro ou None."""
        invalidos = set(campos) - set(self.CAMPOS_ATUALIZAVEIS)
        if invalidos:
            raise ValueError(f"Campos não atualizáveis: {sorted(invalidos)}")
        if not campos:
            raise ValueError("Informe ao menos um campo para atualizar.")

        # Os nomes das colunas vêm da lista fixa acima; os valores vão por parâmetro.
        atribuicoes = ", ".join(f"{coluna} = %s" for coluna in campos)
        sql = f"UPDATE produto SET {atribuicoes} WHERE id = %s RETURNING {self.COLUNAS}"
        linha, _ = self._escrever(sql, (*campos.values(), produto_id))
        return linha

    def deletar(self, produto_id):
        """DELETE: remove o produto. Devolve True se removeu, False se não existia."""
        _, removidos = self._escrever("DELETE FROM produto WHERE id = %s", (produto_id,))
        return removidos > 0
