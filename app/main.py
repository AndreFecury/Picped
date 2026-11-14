from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import registrar_handlers
from app.routers import (
    auth,
    categorias,
    health,
    listas,
    precos,
    produtos,
    supermercados,
    usuarios,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    engine.dispose()  # fecha o pool de conexões ao desligar


DESCRICAO = """
Plataforma inteligente de comparação de preços e economia domésticos.

**Formato de erro** (todas as rotas):
`{"erro": {"codigo": "...", "mensagem": "...", "detalhes": [...]}}`

| Status | Quando |
|---|---|
| 200 | Consulta/atualização bem-sucedida |
| 201 | Registro criado |
| 204 | Registro excluído (sem corpo) |
| 400 | JSON mal formado ou PATCH sem nenhum campo |
| 401 | Rota exige login e o token está ausente, inválido ou expirado |
| 403 | Recurso de outro usuário |
| 404 | Registro ou rota inexistente |
| 409 | Duplicidade ou registro em uso por outros dados |
| 422 | Dados inválidos (schema) ou regra de negócio violada |
"""

TAGS = [
    {"name": "Autenticação", "description": "Login com token Bearer (use o botão Authorize)."},
    {"name": "Categorias", "description": "Categorias de produtos (CRUD)."},
    {"name": "Produtos", "description": "Produtos (CRUD) e comparação de preços entre supermercados."},
    {"name": "Supermercados", "description": "Supermercados (CRUD) e busca pela localização do usuário."},
    {"name": "Preços", "description": "Preços coletados pelos usuários (CRUD) com validação por geolocalização."},
    {"name": "Usuários", "description": "Usuários (CRUD); a senha é guardada apenas como hash."},
    {"name": "Listas de compras", "description": "Listas do usuário logado e em qual mercado a lista sai mais barata."},
    {"name": "Saúde", "description": "Verificação da API e da conexão com o banco."},
]

app = FastAPI(
    title="Picped API",
    description=DESCRICAO,
    version="0.3.0",
    openapi_tags=TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

registrar_handlers(app)

# CORS: permite que clientes web (ex.: versão web do app) chamem a API. O app Android não precisa.
# Autenticação é por cabeçalho Bearer (sem cookies), então allow_credentials fica desligado.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origens,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse(url="/docs")


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(supermercados.router)
app.include_router(usuarios.router)
app.include_router(precos.router)
app.include_router(listas.router)


# Versão web do app Picped (gerada com `flutter build web --base-href /app/` a partir de mobile/).
# Permite usar o app no próprio computador que roda a API: http://localhost:8000/app/
_WEB_APP = Path(__file__).resolve().parent.parent / "web_app"
if _WEB_APP.is_dir():
    app.mount("/app", StaticFiles(directory=_WEB_APP, html=True), name="app_web")
