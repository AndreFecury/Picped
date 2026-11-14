import pytest

from tests.conftest import assert_erro, campos_com_erro

CAMPOS = {"id", "nome", "marca", "unidade_medida", "codigo_barras", "categoria_id"}

NOVO = {
    "nome": "Macarrão Espaguete 500g",
    "marca": "Renata",
    "unidade_medida": "un",
    "codigo_barras": "7896022200103",
    "categoria_id": 7,
}


def test_listar(client):
    resp = client.get("/produtos")
    assert resp.status_code == 200
    assert len(resp.json()) == 12
    assert set(resp.json()[0]) == CAMPOS


def test_obter(client):
    resp = client.get("/produtos/1")
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Arroz Branco Tipo 1 5kg"
    assert resp.json()["categoria_id"] == 1


def test_obter_inexistente_404(client):
    assert_erro(client.get("/produtos/999"), 404, "nao_encontrado")


def test_criar_201(client):
    resp = client.post("/produtos", json=NOVO)
    assert resp.status_code == 201
    corpo = resp.json()
    assert set(corpo) == CAMPOS
    assert {k: corpo[k] for k in NOVO} == NOVO


def test_criar_sem_opcionais_201(client):
    resp = client.post("/produtos", json={"nome": "Alface Crespa", "unidade_medida": "un", "categoria_id": 5})
    assert resp.status_code == 201
    assert resp.json()["marca"] is None
    assert resp.json()["codigo_barras"] is None


def test_regra_categoria_inexistente_422(client):
    erro = assert_erro(client.post("/produtos", json={**NOVO, "categoria_id": 999}), 422, "regra_de_negocio")
    assert "categoria" in erro["mensagem"]


def test_criar_duplicado_nome_marca_409(client):
    dup = {"nome": "Feijão Carioca 1kg", "marca": "Camil", "unidade_medida": "un", "categoria_id": 1}
    assert_erro(client.post("/produtos", json=dup), 409, "registro_duplicado")


def test_criar_codigo_barras_duplicado_409(client):
    assert client.post("/produtos", json=NOVO).status_code == 201
    outro = {**NOVO, "nome": "Outro Macarrão"}
    assert_erro(client.post("/produtos", json=outro), 409, "registro_duplicado")


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("unidade_medida", "caixa"),  # fora do Literal
        ("codigo_barras", "12AB"),  # não é EAN
        ("categoria_id", 0),  # gt=0
        ("categoria_id", "7"),  # validação estrita: string não vira int
        ("nome", "X"),  # min_length
    ],
)
def test_criar_dados_invalidos_422(client, campo, valor):
    resp = client.post("/produtos", json={**NOVO, campo: valor})
    assert_erro(resp, 422, "validacao")
    assert campo in campos_com_erro(resp)


def test_put_substitui_e_limpa_opcionais(client):
    resp = client.put(
        "/produtos/11", json={"nome": "Banana Nanica", "unidade_medida": "kg", "categoria_id": 5}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 11,
        "nome": "Banana Nanica",
        "marca": None,
        "unidade_medida": "kg",
        "codigo_barras": None,
        "categoria_id": 5,
    }


def test_put_inexistente_404(client):
    assert_erro(client.put("/produtos/999", json=NOVO), 404)


def test_put_incompleto_422(client):
    assert_erro(client.put("/produtos/1", json={"nome": "Só o nome"}), 422, "validacao")


def test_patch_parcial(client):
    resp = client.patch("/produtos/1", json={"marca": "Camil"})
    assert resp.status_code == 200
    assert resp.json()["marca"] == "Camil"
    assert resp.json()["nome"] == "Arroz Branco Tipo 1 5kg"  # resto intacto


def test_patch_categoria_inexistente_422(client):
    assert_erro(client.patch("/produtos/1", json={"categoria_id": 999}), 422, "regra_de_negocio")


def test_patch_inexistente_404(client):
    assert_erro(client.patch("/produtos/999", json={"marca": "X"}), 404)


def test_patch_vazio_400(client):
    assert_erro(client.patch("/produtos/1", json={}), 400)


def test_patch_obrigatorio_nulo_422(client):
    assert_erro(client.patch("/produtos/1", json={"nome": None}), 422, "validacao")


def test_deletar_204(client):
    novo = client.post("/produtos", json=NOVO).json()
    assert client.delete(f"/produtos/{novo['id']}").status_code == 204
    assert_erro(client.get(f"/produtos/{novo['id']}"), 404)


def test_deletar_com_precos_409(client):
    assert_erro(client.delete("/produtos/1"), 409, "violacao_de_relacionamento")


def test_deletar_inexistente_404(client):
    assert_erro(client.delete("/produtos/999"), 404)


# ---------- regra de negócio: comparação de preços ----------


def test_comparacao_ordena_e_calcula_economia(client):
    resp = client.get("/produtos/1/comparacao")
    assert resp.status_code == 200
    c = resp.json()
    assert set(c) == {
        "produto_id", "produto_nome", "menor_preco", "maior_preco", "economia", "economia_percentual", "ofertas"
    }
    valores = [o["valor"] for o in c["ofertas"]]
    assert valores == sorted(valores)
    # usa só o preço MAIS RECENTE de cada mercado (Atacadão: 28.50, não 27.90)
    assert valores == [28.50, 31.49, 32.90]
    assert c["menor_preco"]["supermercado_nome"] == "Atacadão"
    assert c["maior_preco"]["supermercado_nome"] == "DB"
    assert c["economia"] == pytest.approx(4.40)
    assert c["economia_percentual"] == pytest.approx(13.37)


def test_comparacao_sem_precos(client):
    novo = client.post("/produtos", json=NOVO).json()
    c = client.get(f"/produtos/{novo['id']}/comparacao").json()
    assert c["ofertas"] == []
    assert c["menor_preco"] is None and c["economia"] == 0


def test_comparacao_produto_inexistente_404(client):
    assert_erro(client.get("/produtos/999/comparacao"), 404)


# ---------- busca (usada pela tela Pesquisar do app) ----------


def test_busca_por_nome_sem_diferenciar_maiusculas(client):
    resp = client.get("/produtos", params={"busca": "ARROZ"})
    assert resp.status_code == 200
    assert [p["nome"] for p in resp.json()] == ["Arroz Branco Tipo 1 5kg"]


def test_busca_por_codigo_de_barras(client):
    criado = client.post("/produtos", json=NOVO).json()
    resp = client.get("/produtos", params={"codigo_barras": NOVO["codigo_barras"]})
    assert [p["id"] for p in resp.json()] == [criado["id"]]


def test_busca_por_categoria(client):
    resp = client.get("/produtos", params={"categoria_id": 1})
    assert resp.status_code == 200
    assert resp.json() and all(p["categoria_id"] == 1 for p in resp.json())


# ---------- histórico de preços ----------


def test_historico_calcula_com_registros_reais(client):
    resp = client.get("/produtos/1/historico")
    assert resp.status_code == 200
    h = resp.json()
    assert h["registros"] == len(h["pontos"]) == 4
    datas = [p["coletado_em"] for p in h["pontos"]]
    assert datas == sorted(datas)  # do mais antigo para o mais recente (eixo do gráfico)
    assert h["minimo"] == pytest.approx(27.90)
    assert h["maximo"] == pytest.approx(32.90)
    assert h["media"] == pytest.approx(30.20)
    assert h["variacao_percentual"] == pytest.approx(2.15)  # 27,90 -> 28,50


def test_historico_sem_registros_nao_inventa_valores(client):
    novo = client.post("/produtos", json=NOVO).json()
    h = client.get(f"/produtos/{novo['id']}/historico").json()
    assert h["registros"] == 0 and h["pontos"] == []
    assert h["minimo"] is None and h["media"] is None and h["variacao_percentual"] is None


def test_historico_produto_inexistente_404(client):
    assert_erro(client.get("/produtos/999/historico"), 404)
