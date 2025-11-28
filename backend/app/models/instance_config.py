from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.base import Base  # ajuste se o caminho do Base for diferente


class InstanceConfig(Base):
    __tablename__ = "instance_configs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # One-to-one com Instance
    instance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instances.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Controle se a instância é gerenciada pela aplicação
    managed = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Se True, esta instância é gerenciada pelo scheduler Stop/Start",
    )

    # CRON defaults (vamos validar sintaxe na camada de serviço)
    default_start_cron = Column(
        String(64),
        nullable=True,
        doc="Expressão CRON padrão para start da instância",
    )
    default_stop_cron = Column(
        String(64),
        nullable=True,
        doc="Expressão CRON padrão para stop da instância",
    )

    # Timezone específico por instância (ex: 'America/Sao_Paulo')
    timezone = Column(
        String(64),
        nullable=False,
        default="UTC",
    )

    # Flag de proteção: não desligar mesmo se gerenciada
    protection_flag = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Se True, bloqueia stop mesmo que o CRON mande desligar",
    )

    # Notas livres para administrador
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationship
    instance = relationship(
        "Instance",
        back_populates="config",
    )

    def __repr__(self) -> str:
        return (
            f"<InstanceConfig id={self.id} instance_id={self.instance_id} "
            f"managed={self.managed} protection_flag={self.protection_flag}>"
        )
