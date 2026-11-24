"""Saúde da API, Swagger e formato centralizado de erros."""
from tests.conftest import assert_erro


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["status"] == "ok" and corpo["banco"] == "ok"
    assert isinstance(corpo["versao"], str) and corpo["versao"]


def test_swagger_disponivel(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "swagger-ui" in resp.text.lower()


def test_openapi_documenta_crud_e_exemplos(client):
    spec = client.get("/openapi.json").json()
    for recurso in ("categorias", "produtos", "supermercados", "usuarios", "precos"):
        assert set(spec["paths"][f"/{recurso}"]) == {"get", "post"}
        assert set(spec["paths"][f"/{recurso}/{{{recurso[:-1]}_id}}"]) == {"get", "put", "patch", "delete"}
    schemas = spec["components"]["schemas"]
    for nome in ("CategoriaCreate", "ProdutoCreate", "SupermercadoCreate", "UsuarioCreate", "PrecoCreate"):
        assert schemas[nome]["examples"], f"{nome} sem exemplo de payload"
    assert "ErroOut" in schemas


def test_rota_inexistente_404_no_formato_padrao(client):
    assert_erro(client.get("/nao-existe"), 404, "nao_encontrado")


def test_metodo_nao_permitido_405(client):
    assert_erro(client.delete("/categorias"), 405, "metodo_nao_permitido")


def test_json_mal_formatado_400(client):
    resp = client.post("/categorias", content='{"nome": "Padaria"', headers={"Content-Type": "application/json"})
    erro = assert_erro(resp, 400, "requisicao_invalida")
    assert erro["detalhes"][0]["campo"] == "body"


def test_id_invalido_na_url_422(client):
    assert_erro(client.get("/produtos/0"), 422, "validacao")
    assert_erro(client.get("/produtos/abc"), 422, "validacao")


def test_paginacao_invalida_422(client):
    assert_erro(client.get("/produtos", params={"limit": 0}), 422, "validacao")
    assert_erro(client.get("/produtos", params={"limit": 500}), 422, "validacao")
