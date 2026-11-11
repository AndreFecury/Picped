import pytest

from app.services.usuario_service import verificar_senha
from tests.conftest import assert_erro, campos_com_erro

CAMPOS = {"id", "nome", "email", "criado_em"}
NOVO = {"nome": "Diego Teste", "email": "diego@picped.dev", "senha": "Senha@123"}


def _hash_no_banco(conexao_admin, usuario_id: int) -> str:
    return conexao_admin.execute("SELECT senha_hash FROM usuario WHERE id = %s", (usuario_id,)).fetchone()[0]


def test_listar_nao_expoe_senha(client):
    resp = client.get("/usuarios")
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    for u in resp.json():
        assert set(u) == CAMPOS


def test_obter(client):
    resp = client.get("/usuarios/1")
    assert resp.status_code == 200
    assert resp.json()["email"] == "ana@picped.dev"
    assert set(resp.json()) == CAMPOS


def test_obter_inexistente_404(client):
    assert_erro(client.get("/usuarios/999"), 404)


def test_criar_201_grava_hash(client, conexao_admin):
    resp = client.post("/usuarios", json={**NOVO, "email": "Diego@Picped.DEV"})
    assert resp.status_code == 201
    corpo = resp.json()
    assert set(corpo) == CAMPOS
    assert corpo["email"] == "diego@picped.dev"  # normalizado
    senha_hash = _hash_no_banco(conexao_admin, corpo["id"])
    assert senha_hash != NOVO["senha"]
    assert senha_hash.startswith("pbkdf2_sha256$")
    assert verificar_senha(NOVO["senha"], senha_hash)


def test_email_duplicado_409(client):
    erro = assert_erro(client.post("/usuarios", json={**NOVO, "email": "ANA@picped.dev"}), 409, "conflito")
    assert "e-mail" in erro["mensagem"]


@pytest.mark.parametrize(
    "campo, valor",
    [("email", "sem-arroba"), ("email", "a@b"), ("senha", "curta"), ("nome", "")],
)
def test_criar_invalido_422(client, campo, valor):
    resp = client.post("/usuarios", json={**NOVO, campo: valor})
    assert_erro(resp, 422, "validacao")
    assert campo in campos_com_erro(resp)


def test_criar_nao_aceita_senha_hash_direto(client):
    resp = client.post("/usuarios", json={**NOVO, "senha_hash": "x"})
    assert_erro(resp, 422, "validacao")


def test_put_substitui_e_troca_senha(client, conexao_admin):
    antigo = _hash_no_banco(conexao_admin, 3)
    dados = {"nome": "Carla Souza", "email": "carla.souza@picped.dev", "senha": "NovaSenha1"}
    resp = client.put("/usuarios/3", json=dados)
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Carla Souza"
    novo = _hash_no_banco(conexao_admin, 3)
    assert novo != antigo and verificar_senha("NovaSenha1", novo)


def test_put_mantem_proprio_email(client):
    resp = client.put("/usuarios/1", json={"nome": "Ana", "email": "ana@picped.dev", "senha": "Senha@123"})
    assert resp.status_code == 200


def test_put_inexistente_404(client):
    assert_erro(client.put("/usuarios/999", json=NOVO), 404)


def test_patch_nome(client):
    resp = client.patch("/usuarios/2", json={"nome": "Bruno Lima"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Bruno Lima"
    assert resp.json()["email"] == "bruno@picped.dev"


def test_patch_email_de_outro_usuario_409(client):
    assert_erro(client.patch("/usuarios/2", json={"email": "ana@picped.dev"}), 409, "conflito")


def test_patch_vazio_400(client):
    assert_erro(client.patch("/usuarios/2", json={}), 400)


def test_patch_inexistente_404(client):
    assert_erro(client.patch("/usuarios/999", json={"nome": "Ninguém"}), 404)


def test_deletar_204(client):
    novo = client.post("/usuarios", json=NOVO).json()
    assert client.delete(f"/usuarios/{novo['id']}").status_code == 204
    assert_erro(client.get(f"/usuarios/{novo['id']}"), 404)


def test_deletar_com_precos_409(client):
    assert_erro(client.delete("/usuarios/1"), 409, "violacao_de_relacionamento")


def test_deletar_inexistente_404(client):
    assert_erro(client.delete("/usuarios/999"), 404)
