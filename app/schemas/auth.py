from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import CreateSchema
from app.schemas.usuario import UsuarioOut


class LoginIn(CreateSchema):
    model_config = ConfigDict(json_schema_extra={"examples": [{"email": "ana@picped.dev", "senha": "picped123"}]})

    email: str = Field(min_length=3, max_length=150)
    senha: str = Field(min_length=1, max_length=72)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em: int = Field(description="Validade do token, em segundos.")
    usuario: UsuarioOut
