"""Fluxo usado pelo aplicativo: login com token, listas de compras e comparação."""
from tests.conftest import assert_erro


def _token(client, email="ana@picped.dev", senha="picped123") -> dict:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_login_e_me(client):
    h = _token(client)
    resp = client.get("/auth/me", headers=h)
    assert resp.status_code == 200
    assert resp.json()["email"] == "ana@picped.dev"


def test_login_senha_errada_401(client):
    resp = client.post("/auth/login", json={"email": "ana@picped.dev", "senha": "errada"})
    assert_erro(resp, 401)


def test_listas_exigem_token(client):
    assert_erro(client.get("/listas"), 401)


def test_fluxo_lista_completo(client):
    h = _token(client)
    lista = client.post("/listas", json={"nome": "Teste APS"}, headers=h)
    assert lista.status_code == 201, lista.text
    lid = lista.json()["id"]

    item = client.post(f"/listas/{lid}/itens", json={"produto_id": 1, "quantidade": 2}, headers=h)
    assert item.status_code == 201, item.text
    repetido = client.post(f"/listas/{lid}/itens", json={"produto_id": 1}, headers=h)
    assert_erro(repetido, 409)

    iid = item.json()["id"]
    marcado = client.patch(f"/listas/{lid}/itens/{iid}", json={"comprado": True}, headers=h)
    assert marcado.status_code == 200 and marcado.json()["comprado"] is True
    assert_erro(client.patch(f"/listas/{lid}/itens/{iid}", json={}, headers=h), 400)

    comp = client.get(f"/listas/{lid}/comparacao", headers=h)
    assert comp.status_code == 200, comp.text

    assert client.delete(f"/listas/{lid}", headers=h).status_code == 204
    assert_erro(client.get(f"/listas/{lid}", headers=h), 404)


def test_lista_de_outro_usuario_inacessivel(client):
    h_ana = _token(client)
    lid = client.post("/listas", json={"nome": "Privada"}, headers=h_ana).json()["id"]
    h_bruno = _token(client, "bruno@picped.dev")
    resp = client.get(f"/listas/{lid}", headers=h_bruno)
    assert resp.status_code in (403, 404)
