"""Base dos schemas de atualização parcial (PATCH)."""
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator


class UpdateSchema(BaseModel):
    """
    No PATCH o campo pode ser omitido, mas campos obrigatórios não podem ser
    enviados como null. Validação feita aqui (entrada), e não deixada para o banco.
    """

    model_config = ConfigDict(extra="forbid")  # rejeita campos desconhecidos
    nao_nulos: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def _sem_null_em_obrigatorios(self):
        nulos = [c for c in self.nao_nulos if c in self.model_fields_set and getattr(self, c) is None]
        if nulos:
            raise ValueError(f"Os campos {', '.join(nulos)} não podem ser nulos.")
        return self
