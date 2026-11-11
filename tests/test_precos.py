import pytest

from tests.conftest import assert_erro, campos_com_erro

CAMPOS = {"id", "produto_id", "supermercado_id", "usuario_id", "valor", "coletado_em", "distancia_metros"}

# Carvalho (id 2) tem raio de 80 m
NOVO = {
    "produto_id": 1,
    "supermercado_id": 2,
    "usuario_id": 1,
    "valor": 29.90,
    "coletado_em": "2026-11-11T09:30:00",
    "distancia_metros": 20,
}


def test_listar_mais_recentes_primeiro(client):
    resp = client.get("/precos", params={"limit": 200})
    assert resp.status_code == 200
    dados = resp.json()
    assert len(dados) == 26
    assert set(dados[0]) == CAMPOS
    datas = [p["coletado_em"] for p in dados]
    assert datas == sorted(datas, reverse=True)


def test_listar_filtrando(client):
    resp = client.get("/precos", params={"produto_id": 1, "supermercado_id": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert all(p["produto_id"] == 1 and p["supermercado_id"] == 1 for p in resp.json())


def test_obter(client):
    resp = client.get("/precos/1")
    assert resp.status_code == 200
    assert set(resp.json()) == CAMPOS


def test_obter_inexistente_404(client):
    assert_erro(client.get("/precos/999"), 404)


def test_criar_201(client):
    resp = client.post("/precos", json=NOVO)
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["valor"] == 29.90
    assert corpo["coletado_em"].startswith("2026-11-11T09:30")


def test_criar_sem_data_usa_agora(client):
    dados = {k: v for k, v in NOVO.items() if k != "coletado_em"}
    resp = client.post("/precos", json=dados)
    assert resp.status_code == 201
    assert resp.json()["coletado_em"]


# ---------- regras de negócio ----------


@pytest.mark.parametrize("campo", ["produto_id", "supermercado_id", "usuario_id"])
def test_regra_referencia_inexistente_422(client, campo):
    erro = assert_erro(client.post("/precos", json={**NOVO, campo: 999}), 422, "regra_de_negocio")
    assert "999" in erro["mensagem"]


def test_regra_supermercado_inativo_422(client):
    client.patch("/supermercados/2", json={"ativo": False})
    erro = assert_erro(client.post("/precos", json=NOVO), 422, "regra_de_negocio")
    assert "inativo" in erro["mensagem"]


def test_regra_fora_do_raio_422(client):
    erro = assert_erro(client.post("/precos", json={**NOVO, "distancia_metros": 81}), 422, "regra_de_negocio")
    assert "80 m" in erro["mensagem"]


def test_regra_no_limite_do_raio_201(client):
    assert client.post("/precos", json={**NOVO, "distancia_metros": 80}).status_code == 201


@pytest.mark.parametrize(
    "campo, valor",
    [("valor", 0), ("valor", -5), ("valor", 1.999), ("distancia_metros", -1), ("produto_id", "1")],
)
def test_criar_invalido_422(client, campo, valor):
    resp = client.post("/precos", json={**NOVO, campo: valor})
    assert_erro(resp, 422, "validacao")
    assert campo in campos_com_erro(resp)


def test_put_substitui_mantendo_data(client):
    original = client.get("/precos/1").json()
    dados = {k: v for k, v in NOVO.items() if k != "coletado_em"}
    resp = client.put("/precos/1", json=dados)
    assert resp.status_code == 200
    assert resp.json()["supermercado_id"] == 2
    assert resp.json()["coletado_em"] == original["coletado_em"]


def test_put_aplica_regras_422(client):
    assert_erro(client.put("/precos/1", json={**NOVO, "distancia_metros": 500}), 422, "regra_de_negocio")


def test_put_inexistente_404(client):
    assert_erro(client.put("/precos/999", json=NOVO), 404)


def test_patch_corrige_valor(client):
    resp = client.patch("/precos/1", json={"valor": 26.99})
    assert resp.status_code == 200
    assert resp.json()["valor"] == 26.99


def test_patch_campo_nao_editavel_422(client):
    # no PATCH só o valor pode ser corrigido
    assert_erro(client.patch("/precos/1", json={"supermercado_id": 3}), 422, "validacao")


def test_patch_vazio_400(client):
    assert_erro(client.patch("/precos/1", json={}), 400)


def test_patch_inexistente_404(client):
    assert_erro(client.patch("/precos/999", json={"valor": 1}), 404)


def test_deletar_204(client):
    assert client.delete("/precos/1").status_code == 204
    assert_erro(client.get("/precos/1"), 404)


def test_deletar_inexistente_404(client):
    assert_erro(client.delete("/precos/999"), 404)


def test_novo_preco_muda_a_comparacao(client):
    # registra um preço mais barato no DB: ele passa a ser o menor
    client.post("/precos", json={**NOVO, "supermercado_id": 3, "valor": 20.00, "distancia_metros": 10})
    c = client.get("/produtos/1/comparacao").json()
    assert c["menor_preco"]["supermercado_nome"] == "DB"
    assert c["menor_preco"]["valor"] == 20.00
