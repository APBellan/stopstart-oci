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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.base import Base  # ajuste se o caminho do Base for diferente


class Compartment(Base):
    __tablename__ = "compartments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # OCI identifiers
    tenancy_ocid = Column(String(255), nullable=False, index=True)
    compartment_ocid = Column(String(255), nullable=False, unique=True, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Tree structure
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("compartments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent_ocid = Column(String(255), nullable=True, index=True)

    # Path style: /tenancy-name/parent/child
    path = Column(String(1024), nullable=False, index=True)

    is_tenancy_root = Column(Boolean, nullable=False, default=False)

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
    parent = relationship(
        "Compartment",
        remote_side="Compartment.id",
        back_populates="children",
    )

    children = relationship(
        "Compartment",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    instances = relationship(
        "Instance",
        back_populates="compartment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Garante unicidade de path dentro da tenancy
        UniqueConstraint(
            "tenancy_ocid",
            "path",
            name="uq_compartments_tenancy_path",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Compartment id={self.id} name={self.name!r} "
            f"compartment_ocid={self.compartment_ocid!r}>"
        )
