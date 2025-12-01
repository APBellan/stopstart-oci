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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..db.base_class import Base
# ou, se preferir absoluto:
# from app.db.base_class import Base


class Instance(Base):
    __tablename__ = "instances"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # OCI identifiers
    instance_ocid = Column(String(255), nullable=False, unique=True, index=True)
    compartment_ocid = Column(String(255), nullable=False, index=True)

    # FK para Compartment
    compartment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("compartments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    display_name = Column(String(255), nullable=False, index=True)
    region = Column(String(64), nullable=False, index=True)
    availability_domain = Column(String(128), nullable=True)
    fault_domain = Column(String(64), nullable=True)
    shape = Column(String(128), nullable=True)
    lifecycle_state = Column(String(64), nullable=True, index=True)

    # Networking / opcional (podemos expandir depois)
    hostname = Column(String(255), nullable=True)
    private_ip = Column(String(64), nullable=True)
    public_ip = Column(String(64), nullable=True)

    # Tags OCI
    freeform_tags = Column(JSONB, nullable=True)
    defined_tags = Column(JSONB, nullable=True)

    # Metadata opcional
    image_ocid = Column(String(255), nullable=True)
    compartment_path_cache = Column(
        String(1024),
        nullable=True,
        doc="cache do path do compartment para facilitar filtros",
    )

    # Ativo / inativo (para quando some do OCI)
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

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

    # Relationships
    compartment = relationship(
        "Compartment",
        back_populates="instances",
    )

    config = relationship(
        "InstanceConfig",
        back_populates="instance",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Instance id={self.id} display_name={self.display_name!r} "
            f"instance_ocid={self.instance_ocid!r}>"
        )
