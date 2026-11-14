# =====================================================================
# Picped API - Dockerfile multi-stage
#   Estágio 1 (builder): instala as dependências num virtualenv
#   Estágio 2 (test):    builder + dependências de teste + tests/ (usado só no compose --profile test)
#   Estágio 3 (runtime): imagem enxuta, só com o venv + código, rodando como usuário não-root
# =====================================================================

# ---------- Estágio 1: build ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copiar só o requirements primeiro aproveita o cache de camadas do Docker
COPY requirements.txt .
RUN pip install -r requirements.txt


# ---------- Estágio 2: testes (não vai para a imagem final) ----------
FROM builder AS test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests

CMD ["pytest", "-v"]


# ---------- Estágio 3: runtime ----------
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="picped-api" \
      org.opencontainers.image.description="Plataforma inteligente de comparação de preços e economia domésticos"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# usuário de sistema sem shell e sem senha (boas práticas: nunca rodar como root)
RUN groupadd --system --gid 10001 picped \
 && useradd --system --uid 10001 --gid picped --no-create-home --shell /usr/sbin/nologin picped

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=picped:picped app ./app
# versão web do app (servida em /app/)
COPY --chown=picped:picped web_app ./web_app

USER picped

EXPOSE 8000

# o próprio container informa se a API (e o banco) estão respondendo
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
