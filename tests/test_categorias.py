from tests.conftest import assert_erro, campos_com_erro


def test_listar(client):
    resp = client.get("/categorias")
    assert resp.status_code == 200
    dados = resp.json()
    assert len(dados) == 7
    assert set(dados[0]) == {"id", "nome"}


def test_listar_paginado(client):
    resp = client.get("/categorias", params={"limit": 2, "offset": 1})
    assert resp.status_code == 200
    assert [c["id"] for c in resp.json()] == [2, 3]


def test_obter(client):
    resp = client.get("/categorias/2")
    assert resp.status_code == 200
    assert resp.json() == {"id": 2, "nome": "Laticínios"}


def test_obter_inexistente_404(client):
    assert_erro(client.get("/categorias/999"), 404, "nao_encontrado")


def test_criar_201_normaliza_nome(client):
    resp = client.post("/categorias", json={"nome": "  Padaria   e  Doces "})
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["nome"] == "Padaria e Doces"
    assert isinstance(corpo["id"], int)
    assert client.get(f"/categorias/{corpo['id']}").status_code == 200


def test_criar_duplicada_409(client):
    assert_erro(client.post("/categorias", json={"nome": "Bebidas"}), 409, "registro_duplicado")


def test_criar_sem_nome_422(client):
    resp = client.post("/categorias", json={})
    assert_erro(resp, 422, "validacao")
    assert "nome" in campos_com_erro(resp)


def test_criar_nome_curto_422(client):
    assert_erro(client.post("/categorias", json={"nome": "A"}), 422, "validacao")


def test_criar_campo_desconhecido_422(client):
    resp = client.post("/categorias", json={"nome": "Padaria", "cor": "azul"})
    assert_erro(resp, 422, "validacao")
    assert "cor" in campos_com_erro(resp)


def test_put_substitui(client):
    resp = client.put("/categorias/3", json={"nome": "Bebidas e Sucos"})
    assert resp.status_code == 200
    assert resp.json() == {"id": 3, "nome": "Bebidas e Sucos"}


def test_put_inexistente_404(client):
    assert_erro(client.put("/categorias/999", json={"nome": "Qualquer"}), 404)


def test_put_sem_campo_obrigatorio_422(client):
    assert_erro(client.put("/categorias/3", json={}), 422, "validacao")


def test_patch_atualiza(client):
    resp = client.patch("/categorias/1", json={"nome": "Grãos"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Grãos"


def test_patch_vazio_400(client):
    assert_erro(client.patch("/categorias/1", json={}), 400, "requisicao_invalida")


def test_patch_nome_nulo_422(client):
    assert_erro(client.patch("/categorias/1", json={"nome": None}), 422, "validacao")


def test_patch_para_nome_existente_409(client):
    assert_erro(client.patch("/categorias/1", json={"nome": "Bebidas"}), 409, "registro_duplicado")


def test_deletar_204(client):
    nova = client.post("/categorias", json={"nome": "Temporária"}).json()
    resp = client.delete(f"/categorias/{nova['id']}")
    assert resp.status_code == 204
    assert resp.content == b""
    assert_erro(client.get(f"/categorias/{nova['id']}"), 404)


def test_deletar_inexistente_404(client):
    assert_erro(client.delete("/categorias/999"), 404, "nao_encontrado")


def test_deletar_em_uso_409(client):
    # categoria 1 tem produtos vinculados (FK)
    assert_erro(client.delete("/categorias/1"), 409, "violacao_de_relacionamento")
