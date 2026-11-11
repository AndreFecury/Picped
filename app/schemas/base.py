"""
Bases dos schemas Pydantic de entrada.

Validação estrita:
- extra="forbid": campos desconhecidos são rejeitados (422);
- strict=True: sem conversão silenciosa de tipos ("5" não vira 5, "true" não vira True);
- str_strip_whitespace: espaços nas pontas são removidos antes de validar o tamanho.
"""
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator

CONFIG_ENTRADA = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class CreateSchema(BaseModel):
    """Base dos payloads de criação (POST)."""

    model_config = CONFIG_ENTRADA


class UpdateSchema(BaseModel):
    """
    Base dos payloads de atualização parcial (PATCH).
    O campo pode ser omitido, mas campos obrigatórios não podem ser enviados como null.
    Validação feita aqui (entrada), e não deixada para o banco.
    """

    model_config = CONFIG_ENTRADA
    nao_nulos: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def _sem_null_em_obrigatorios(self):
        nulos = [c for c in self.nao_nulos if c in self.model_fields_set and getattr(self, c) is None]
        if nulos:
            raise ValueError(f"Os campos {', '.join(nulos)} não podem ser nulos.")
        return self
