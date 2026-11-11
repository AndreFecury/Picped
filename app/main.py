from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.database import engine
from app.core.exceptions import registrar_handlers
from app.routers import categorias, health, precos, produtos, supermercados, usuarios


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
| 404 | Registro ou rota inexistente |
| 409 | Duplicidade ou registro em uso por outros dados |
| 422 | Dados inválidos (schema) ou regra de negócio violada |
"""

TAGS = [
    {"name": "Categorias", "description": "Categorias de produtos (CRUD)."},
    {"name": "Produtos", "description": "Produtos (CRUD) e comparação de preços entre supermercados."},
    {"name": "Supermercados", "description": "Supermercados (CRUD) e busca pela localização do usuário."},
    {"name": "Preços", "description": "Preços coletados pelos usuários (CRUD) com validação por geolocalização."},
    {"name": "Usuários", "description": "Usuários (CRUD); a senha é guardada apenas como hash."},
    {"name": "Saúde", "description": "Verificação da API e da conexão com o banco."},
]

app = FastAPI(
    title="Picped API",
    description=DESCRICAO,
    version="0.2.0",
    openapi_tags=TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

registrar_handlers(app)


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse(url="/docs")


app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(supermercados.router)
app.include_router(precos.router)
app.include_router(usuarios.router)
