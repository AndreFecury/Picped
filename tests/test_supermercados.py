import pytest

from tests.conftest import assert_erro, campos_com_erro

CAMPOS = {"id", "nome", "cidade", "bairro", "endereco", "latitude", "longitude", "raio_metros", "ativo"}

NOVO = {
    "nome": "Assaí Atacadista",
    "cidade": "Manaus",
    "bairro": "Japiim",
    "endereco": "Av. Rodrigo Otávio, 1000",
    "latitude": -3.1245,
    "longitude": -59.9853,
    "raio_metros": 120,
    "ativo": True,
}


def test_listar(client):
    resp = client.get("/supermercados")
    assert resp.status_code == 200
    assert len(resp.json()) == 5
    assert set(resp.json()[0]) == CAMPOS


def test_obter(client):
    resp = client.get("/supermercados/2")
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Carvalho"
    assert resp.json()["latitude"] == pytest.approx(-3.1115)


def test_obter_inexistente_404(client):
    assert_erro(client.get("/supermercados/999"), 404)


def test_criar_201(client):
    resp = client.post("/supermercados", json=NOVO)
    assert resp.status_code == 201
    assert set(resp.json()) == CAMPOS
    assert resp.json()["nome"] == "Assaí Atacadista"


def test_criar_usa_padroes(client):
    dados = {k: v for k, v in NOVO.items() if k not in ("raio_metros", "ativo", "endereco")}
    corpo = client.post("/supermercados", json=dados).json()
    assert corpo["raio_metros"] == 80
    assert corpo["ativo"] is True
    assert corpo["endereco"] is None


def test_criar_duplicado_409(client):
    dup = {**NOVO, "nome": "Carvalho", "bairro": "Adrianópolis"}
    assert_erro(client.post("/supermercados", json=dup), 409, "registro_duplicado")


@pytest.mark.parametrize(
    "campo, valor",
    [("latitude", -91), ("longitude", 181), ("raio_metros", 0), ("raio_metros", 10000), ("ativo", "sim")],
)
def test_criar_invalido_422(client, campo, valor):
    resp = client.post("/supermercados", json={**NOVO, campo: valor})
    assert_erro(resp, 422, "validacao")
    assert campo in campos_com_erro(resp)


def test_put_substitui(client):
    resp = client.put("/supermercados/5", json={**NOVO, "nome": "Super Mais Flores"})
    assert resp.status_code == 200
    assert resp.json()["id"] == 5
    assert resp.json()["nome"] == "Super Mais Flores"
    assert resp.json()["raio_metros"] == 120


def test_put_inexistente_404(client):
    assert_erro(client.put("/supermercados/999", json=NOVO), 404)


def test_patch_desativa(client):
    resp = client.patch("/supermercados/1", json={"ativo": False})
    assert resp.status_code == 200
    assert resp.json()["ativo"] is False


def test_patch_vazio_400(client):
    assert_erro(client.patch("/supermercados/1", json={}), 400)


def test_patch_inexistente_404(client):
    assert_erro(client.patch("/supermercados/999", json={"ativo": False}), 404)


def test_deletar_204(client):
    novo = client.post("/supermercados", json=NOVO).json()
    assert client.delete(f"/supermercados/{novo['id']}").status_code == 204
    assert_erro(client.get(f"/supermercados/{novo['id']}"), 404)


def test_deletar_com_precos_409(client):
    assert_erro(client.delete("/supermercados/1"), 409, "violacao_de_relacionamento")


def test_deletar_inexistente_404(client):
    assert_erro(client.delete("/supermercados/999"), 404)


# ---------- regra de negócio: geolocalização ----------


def test_proximos_encontra_mercado_na_posicao(client):
    resp = client.get("/supermercados/proximos", params={"latitude": -3.1115, "longitude": -60.0128})
    assert resp.status_code == 200
    assert resp.json()[0] == {"id": 2, "nome": "Carvalho", "distancia_metros": 0}


def test_proximos_fora_de_qualquer_raio(client):
    resp = client.get("/supermercados/proximos", params={"latitude": -3.20, "longitude": -60.20})
    assert resp.status_code == 200
    assert resp.json() == []


def test_proximos_ignora_mercado_inativo(client):
    client.patch("/supermercados/2", json={"ativo": False})
    resp = client.get("/supermercados/proximos", params={"latitude": -3.1115, "longitude": -60.0128})
    assert resp.json() == []


def test_proximos_coordenada_invalida_422(client):
    assert_erro(client.get("/supermercados/proximos", params={"latitude": 100, "longitude": 0}), 422)
    assert_erro(client.get("/supermercados/proximos"), 422)
