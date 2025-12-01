# app/schemas/instance_config.py

from __future__ import annotations

from datetime import time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InstanceConfigBase(BaseModel):
    """
    Campos comuns de configuração de instância.

    Ajuste os campos de agendamento/parametrização para bater 100% com o
    modelo SQLAlchemy InstanceConfig que você já tem.
    """

    managed: bool = Field(
        False,
        description="Se a instância é gerenciada (stop/start automático) pela aplicação.",
    )
    protection_flag: bool = Field(
        False,
        description="Se a instância está protegida contra operações automáticas.",
    )

    # ====== EXEMPLOS de campos de agendamento (ajuste para o seu modelo real) ======
    start_time: Optional[time] = Field(
        None,
        description="Horário diário de start automático (no timezone configurado).",
    )
    stop_time: Optional[time] = Field(
        None,
        description="Horário diário de stop automático (no timezone configurado).",
    )
    timezone: Optional[str] = Field(
        None,
        description="Timezone IANA utilizado para o agendamento (ex.: 'America/Sao_Paulo').",
    )
    days_of_week: Optional[List[str]] = Field(
        default=None,
        description="Lista de dias da semana em que o agendamento se aplica (ex.: ['mon', 'tue']).",
    )
    # ============================================================================
    # Se no seu modelo existir algo como "custom_schedule", "window_start", etc,
    # adicione aqui com o mesmo nome para facilitar o .model_validate(cfg).
    # ============================================================================


class InstanceConfigUpdate(InstanceConfigBase):
    """
    Payload de upsert de configuração de instância (PUT).

    Aqui você pode tornar alguns campos opcionais se quiser permitir updates parciais
    (usando exclude_unset=True na hora de aplicar no modelo).
    Por simplicidade, estou mantendo igual ao base.
    """
    pass


class InstanceConfigResponse(InstanceConfigBase):
    """
    Schema de resposta para configuração de instância.

    - instance_id: chave da instância (FK para instances.id)
    - configurado: True se existe registro persistido, False se é retorno default.
    """

    model_config = ConfigDict(from_attributes=True)

    instance_id: str = Field(
        ...,
        description="Identificador da instância (igual ao da tabela instances).",
    )
    configurado: bool = Field(
        False,
        description=(
            "True se há um registro real em InstanceConfig para esta instância; "
            "False se os valores são default (sem configuração persistida)."
        ),
    )
