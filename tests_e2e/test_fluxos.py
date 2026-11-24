"""
Testes de ponta a ponta contra uma API rodando de verdade (HTTP real).

Rodam em dois momentos do pipeline:
  1. no CI, contra a API local (uvicorn + PostgreSQL do job);
  2. depois do deploy, contra o endereço público (Render + Neon).

Cada fluxo cria os próprios dados (usuário, mercado, lista) com um sufixo único e apaga tudo no
final, para não sujar os dados de demonstração. Uso:
    E2E_BASE_URL=https://picped-api.onrender.com pytest tests_e2e -v
"""
import os
import time
import uuid

import httpx
import pytest

BASE = os.getenv("E2E_BASE_URL", "http://localhost:8000").rstrip("/")
SUFIXO = uuid.uuid4().hex[:8]
SENHA = "e2e-" + uuid.uuid4().hex[:12]
# Carvalho, no seed: -3.111500, -60.012800, raio de 80 m
CARVALHO = {"latitude": -3.1115, "longitude": -60.0128}


@pytest.fixture(scope="session")
def api():
    # o plano grátis do Render dorme sem uso: a primeira chamada pode levar ~1 min
    with httpx.Client(base_url=BASE, timeout=httpx.Timeout(90.0, connect=90.0), follow_redirects=True) as c:
        for _ in range(6):
            try:
                if c.get("/health").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(10)
        yield c


@pytest.fixture(scope="session")
def conta(api):
    """Cria um usuário só para esta execução e o exclui (LGPD) no final."""
    email = f"e2e-{SUFIXO}@picped.dev"
    r = api.post("/usuarios", json={"nome": f"Teste E2E {SUFIXO}", "email": email, "senha": SENHA})
    assert r.status_code == 201, r.text
    login = api.post("/auth/login", json={"email": email, "senha": SENHA})
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    yield {"id": r.json()["id"], "email": email, "headers": headers}
    api.delete("/auth/me", headers=headers)


# ---------------------------------------------------------------- infraestrutura
def test_saude_e_banco(api):
    r = api.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok" and r.json()["banco"] == "ok"


def test_documentacao_swagger(api):
    assert api.get("/docs").status_code == 200
    spec = api.get("/openapi.json").json()
    assert sum(len(v) for v in spec["paths"].values()) >= 46


def test_versao_web_do_app(api):
    r = api.get("/app/")
    assert r.status_code == 200 and "flutter" in r.text.lower()


def test_erro_no_formato_padrao(api):
    r = api.get("/rota-que-nao-existe")
    assert r.status_code == 404 and r.json()["erro"]["codigo"] == "nao_encontrado"


# ---------------------------------------------------------------- conta e login
def test_login_com_senha_errada(api, conta):
    r = api.post("/auth/login", json={"email": conta["email"], "senha": "senha-errada"})
    assert r.status_code == 401


def test_usuario_logado(api, conta):
    r = api.get("/auth/me", headers=conta["headers"])
    assert r.status_code == 200 and r.json()["email"] == conta["email"]


def test_rota_protegida_sem_token(api):
    assert api.get("/listas").status_code == 401


# ---------------------------------------------------------------- catálogo e comparação
def test_busca_de_produto(api):
    r = api.get("/produtos", params={"busca": "arroz"})
    assert r.status_code == 200 and any("Arroz" in p["nome"] for p in r.json())


def test_comparacao_de_precos_do_produto(api):
    c = api.get("/produtos/1/comparacao").json()
    valores = [o["valor"] for o in c["ofertas"]]
    assert valores == sorted(valores) and len(valores) >= 2
    assert c["economia"] >= 0


def test_historico_de_precos(api):
    h = api.get("/produtos/1/historico").json()
    assert h["registros"] >= 1 and h["minimo"] <= h["media"] <= h["maximo"]


def test_categorias(api):
    r = api.get("/categorias")
    assert r.status_code == 200 and len(r.json()) >= 1


def test_mercados_proximos_pelo_gps(api):
    r = api.get("/supermercados/proximos", params=CARVALHO)
    assert r.status_code == 200 and any(m["nome"] == "Carvalho" for m in r.json())


# ---------------------------------------------------------------- registrar preço (regra do GPS)
@pytest.fixture(scope="session")
def mercado_teste(api):
    """Mercado próprio do teste, para não alterar as comparações da demonstração."""
    r = api.post("/supermercados", json={
        "nome": f"Mercado E2E {SUFIXO}", "cidade": "Manaus", "bairro": "Teste",
        "latitude": -3.2000, "longitude": -60.2000, "raio_metros": 80,
    })
    assert r.status_code == 201, r.text
    yield r.json()
    api.delete(f"/supermercados/{r.json()['id']}")


def test_registrar_preco_dentro_do_raio(api, conta, mercado_teste):
    r = api.post("/precos", headers=conta["headers"], json={
        "produto_id": 1, "supermercado_id": mercado_teste["id"], "usuario_id": conta["id"],
        "valor": 29.90, "distancia_metros": 20,
    })
    assert r.status_code == 201, r.text
    assert api.delete(f"/precos/{r.json()['id']}").status_code == 204


def test_preco_fora_do_raio_e_recusado(api, conta, mercado_teste):
    r = api.post("/precos", headers=conta["headers"], json={
        "produto_id": 1, "supermercado_id": mercado_teste["id"], "usuario_id": conta["id"],
        "valor": 29.90, "distancia_metros": 500,
    })
    assert r.status_code == 422 and r.json()["erro"]["codigo"] == "regra_de_negocio"


def test_preco_em_nome_de_outro_usuario_e_bloqueado(api, conta, mercado_teste):
    r = api.post("/precos", headers=conta["headers"], json={
        "produto_id": 1, "supermercado_id": mercado_teste["id"], "usuario_id": 1,
        "valor": 29.90, "distancia_metros": 20,
    })
    assert r.status_code == 403


# ---------------------------------------------------------------- listas de compras
def test_fluxo_completo_da_lista(api, conta):
    h = conta["headers"]
    lista = api.post("/listas", headers=h, json={"nome": f"Lista E2E {SUFIXO}"})
    assert lista.status_code == 201, lista.text
    lid = lista.json()["id"]
    try:
        item = api.post(f"/listas/{lid}/itens", headers=h, json={"produto_id": 1, "quantidade": 2})
        assert item.status_code == 201, item.text
        iid = item.json()["id"]
        assert api.patch(f"/listas/{lid}/itens/{iid}", headers=h, json={"comprado": True}).json()["comprado"] is True
        comp = api.get(f"/listas/{lid}/comparacao", headers=h)
        assert comp.status_code == 200 and comp.json()["total_itens"] == 1
        assert comp.json()["melhor_opcao"] is not None
    finally:
        assert api.delete(f"/listas/{lid}", headers=h).status_code == 204
    assert api.get(f"/listas/{lid}", headers=h).status_code == 404
