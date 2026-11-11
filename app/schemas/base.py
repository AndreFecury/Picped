"""Bases dos schemas de entrada: validação estrita, igual para todos os recursos."""
from typing import Annotated, ClassVar

from fastapi import Path
from pydantic import BaseModel, ConfigDict, model_validator

# id na URL: inteiro positivo (GET /produtos/0 -> 422, sem ir ao banco)
IdPath = Annotated[int, Path(gt=0, description="Identificador do registro", examples=[1])]


class EntradaSchema(BaseModel):
    """
    - extra="forbid": campo desconhecido no JSON -> 422 (evita erro de digitação passar em silêncio)
    - str_strip_whitespace: remove espaços do início/fim antes de validar tamanho
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UpdateSchema(EntradaSchema):
    """
    No PATCH o campo pode ser omitido, mas campos obrigatórios não podem ser
    enviados como null. Validação feita aqui (entrada), e não deixada para o banco.
    """

    nao_nulos: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def _sem_null_em_obrigatorios(self):
        nulos = [c for c in self.nao_nulos if c in self.model_fields_set and getattr(self, c) is None]
        if nulos:
            raise ValueError(f"Os campos {', '.join(nulos)} não podem ser nulos.")
        return self
