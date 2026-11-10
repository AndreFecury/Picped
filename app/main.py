from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.core.exceptions import registrar_handlers
from app.routers import categorias, health, precos, produtos, supermercados


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    engine.dispose()  # fecha o pool de conexões ao desligar


app = FastAPI(
    title="Picped API",
    description="Plataforma inteligente de comparação de preços e economia domésticos.",
    version="0.1.0",
    lifespan=lifespan,
)

registrar_handlers(app)

app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(supermercados.router)
app.include_router(precos.router)
