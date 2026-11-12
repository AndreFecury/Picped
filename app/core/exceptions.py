"""Exceções da aplicação e tratamento centralizado de erros (um único formato de resposta)."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("picped")


class AppError(Exception):
    status_code = 500
    codigo = "erro_interno"

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class BadRequestError(AppError):
    status_code = 400
    codigo = "requisicao_invalida"


class UnauthorizedError(AppError):
    status_code = 401
    codigo = "nao_autenticado"


class ForbiddenError(AppError):
    status_code = 403
    codigo = "acesso_negado"


class NotFoundError(AppError):
    status_code = 404
    codigo = "nao_encontrado"


class ConflictError(AppError):
    status_code = 409
    codigo = "conflito"


class BusinessRuleError(AppError):
    status_code = 422
    codigo = "regra_de_negocio"


# SQLSTATE do PostgreSQL -> (status HTTP, código, mensagem)
_ERROS_DE_INTEGRIDADE = {
    "23505": (409, "registro_duplicado", "Já existe um registro com esses dados."),
    "23503": (
        409,
        "violacao_de_relacionamento",
        "Operação inválida: referência inexistente ou registro em uso por outros dados.",
    ),
    "23502": (422, "campo_obrigatorio", "Um campo obrigatório não foi informado."),
    "23514": (422, "dado_invalido", "Os dados violam uma regra de validação do banco."),
}


def _resposta(status: int, codigo: str, mensagem: str, detalhes: list | None = None) -> JSONResponse:
    corpo: dict = {"erro": {"codigo": codigo, "mensagem": mensagem}}
    if detalhes:
        corpo["erro"]["detalhes"] = detalhes
    return JSONResponse(status_code=status, content=corpo)


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        resposta = _resposta(exc.status_code, exc.codigo, exc.mensagem)
        if exc.status_code == 401:
            resposta.headers["WWW-Authenticate"] = "Bearer"
        return resposta

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, exc: RequestValidationError):
        erros = exc.errors()
        # JSON que nem chega a ser lido é requisição mal formada (400), não dado inválido (422)
        if any(e["type"] == "json_invalid" for e in erros):
            return _resposta(400, "json_invalido", "O corpo da requisição não é um JSON válido.")
        detalhes = []
        for e in erros:
            campo = ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0])
            mensagem = e["msg"].removeprefix("Value error, ")
            detalhes.append({"campo": campo, "mensagem": mensagem})
        return _resposta(422, "validacao", "Dados de entrada inválidos.", detalhes)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        # rotas inexistentes (404), método não permitido (405) etc. no mesmo formato
        codigos = {404: "nao_encontrado", 405: "metodo_nao_permitido"}
        mensagens = {404: "Rota não encontrada.", 405: "Método HTTP não permitido nesta rota."}
        return _resposta(
            exc.status_code,
            codigos.get(exc.status_code, "erro_http"),
            mensagens.get(exc.status_code, str(exc.detail)),
        )

    @app.exception_handler(IntegrityError)
    async def _integridade(_: Request, exc: IntegrityError):
        sqlstate = getattr(exc.orig, "sqlstate", None)
        status, codigo, mensagem = _ERROS_DE_INTEGRIDADE.get(
            sqlstate, (409, "violacao_de_integridade", "Operação viola a integridade dos dados.")
        )
        logger.warning("Violação de integridade (%s): %s", sqlstate, exc.orig)
        return _resposta(status, codigo, mensagem)

    @app.exception_handler(DataError)
    async def _dado_invalido(_: Request, exc: DataError):
        logger.warning("Dado inválido: %s", exc.orig)
        return _resposta(422, "dado_invalido", "Valor fora do intervalo ou em formato inválido.")

    @app.exception_handler(OperationalError)
    async def _banco_indisponivel(_: Request, exc: OperationalError):
        logger.error("Banco indisponível: %s", exc.orig)
        return _resposta(503, "banco_indisponivel", "Banco de dados indisponível no momento.")

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, exc: Exception):
        logger.exception("Erro inesperado", exc_info=exc)
        return _resposta(500, "erro_interno", "Erro interno do servidor.")
