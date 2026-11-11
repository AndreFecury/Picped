from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.core.exceptions import registrar_handlers
from app.routers import categorias, health, precos, produtos, supermercados, usuarios


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    engine.dispose()  # fecha o pool de conexões ao desligar


app = FastAPI(
    title="Picped API",
    description=(
        "Plataforma inteligente de comparação de preços e economia domésticos.\n\n"
        "Todas as respostas de erro seguem o formato "
        "`{\"erro\": {\"codigo\", \"mensagem\", \"detalhes\"}}`."
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Saúde", "description": "Status da API e do banco"},
        {"name": "Categorias", "description": "Categorias de produtos"},
        {"name": "Produtos", "description": "Produtos e comparação de preços"},
        {"name": "Supermercados", "description": "Supermercados e geolocalização"},
        {"name": "Usuários", "description": "Usuários que registram preços"},
        {"name": "Preços", "description": "Histórico de preços coletados"},
    ],
    lifespan=lifespan,
)

registrar_handlers(app)

app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(supermercados.router)
app.include_router(usuarios.router)
app.include_router(precos.router)
