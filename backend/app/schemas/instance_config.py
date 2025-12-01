# app/schemas/instance_config.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InstanceConfigBase(BaseModel):
    """
    Campos de configuração de instância, alinhados ao modelo SQLAlchemy InstanceConfig.
    """

    managed: bool = Field(
        False,
        description="Se a instância é gerenciada (stop/start automático) pela aplicação.",
    )

    protection_flag: bool = Field(
        False,
        description="Se a instância está protegida contra operações automáticas (bloqueia stop).",
    )

    default_start_cron: Optional[str] = Field(
        None,
        description="Expressão CRON padrão para start da instância.",
        examples=["0 8 * * 1-5"],
    )

    default_stop_cron: Optional[str] = Field(
        None,
        description="Expressão CRON padrão para stop da instância.",
        examples=["0 20 * * 1-5"],
    )

    timezone: str = Field(
        "UTC",
        description="Timezone IANA utilizado para o agendamento (ex.: 'America/Sao_Paulo').",
    )

    notes: Optional[str] = Field(
        None,
        description="Notas livres para administrador sobre a configuração desta instância.",
    )


class InstanceConfigUpdate(BaseModel):
    """
    Payload de upsert/atualização da configuração (PUT).

    Todos os campos são opcionais para permitir updates parciais.
    No serviço usamos exclude_unset=True para aplicar só o que veio no payload.
    """

    managed: Optional[bool] = Field(
        None,
        description="Se a instância é gerenciada (stop/start automático) pela aplicação.",
    )

    protection_flag: Optional[bool] = Field(
        None,
        description="Se a instância está protegida contra operações automáticas (bloqueia stop).",
    )

    default_start_cron: Optional[str] = Field(
        None,
        description="Expressão CRON padrão para start da instância.",
        examples=["0 8 * * 1-5"],
    )

    default_stop_cron: Optional[str] = Field(
        None,
        description="Expressão CRON padrão para stop da instância.",
        examples=["0 20 * * 1-5"],
    )

    timezone: Optional[str] = Field(
        None,
        description="Timezone IANA utilizado para o agendamento (ex.: 'America/Sao_Paulo').",
    )

    notes: Optional[str] = Field(
        None,
        description="Notas livres para administrador sobre a configuração desta instância.",
    )


class InstanceConfigResponse(InstanceConfigBase):
    """
    Schema de resposta para configuração de instância.

    - instance_id: chave da instância (FK para instances.id, UUID).
    - configurado: True se existe registro persistido em InstanceConfig;
                   False se é retorno default (sem registro no banco).
    """

    model_config = ConfigDict(from_attributes=True)

    instance_id: UUID = Field(
        ...,
        description="Identificador da instância (igual ao da tabela instances, UUID).",
    )

    configurado: bool = Field(
        False,
        description=(
            "True se há um registro real em InstanceConfig para esta instância; "
            "False se os valores são default (sem configuração persistida)."
        ),
    )
