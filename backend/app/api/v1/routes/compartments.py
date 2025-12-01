from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_db
from app.models.tenancy import Tenancy
from app.models.compartment import Compartment
from app.models.instance import Instance
from app.models.instance_config import InstanceConfig
from app.schemas.compartment_navigation import (
    CompartmentNavigationResponse,
    CompartmentBase,
    CompartmentBreadcrumb,
    InstanceWithConfig,
)

router = APIRouter(prefix="/tenancies/{tenancy_id}/compartments", tags=["compartments"])


def _get_tenancy_or_404(db: Session, tenancy_id):
    tenancy = db.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
    if not tenancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenancy não encontrada",
        )
    return tenancy


def _get_root_compartment(db: Session, tenancy_id):
    """
    Considerando que o root compartment é aquele com parent_ocid == None
    dentro da tenancy. Ajuste se na sua modelagem for diferente.
    """
    root = (
        db.query(Compartment)
        .filter(
            Compartment.tenancy_id == tenancy_id,
            Compartment.parent_ocid.is_(None),
        )
        .first()
    )
    if not root:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root compartment não encontrado para esta tenancy",
        )
    return root


def _get_compartment_or_404(db: Session, tenancy_id, compartment_ocid: str):
    compartment = (
        db.query(Compartment)
        .filter(
            Compartment.tenancy_id == tenancy_id,
            Compartment.ocid == compartment_ocid,
        )
        .first()
    )
    if not compartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compartment não encontrado para esta tenancy",
        )
    return compartment


def _build_breadcrumbs(db: Session, tenancy_id, compartment: Compartment) -> List[CompartmentBreadcrumb]:
    """
    Sobe na hierarquia a partir do compartment atual até o root,
    montando a trilha (root -> ... -> current).
    """
    breadcrumbs: List[CompartmentBreadcrumb] = []

    current = compartment
    visited = set()

    while current is not None and current.ocid not in visited:
        visited.add(current.ocid)
        breadcrumbs.append(
            CompartmentBreadcrumb(
                ocid=current.ocid,
                name=current.name,
            )
        )

        if current.parent_ocid is None:
            break

        current = (
            db.query(Compartment)
            .filter(
                Compartment.tenancy_id == tenancy_id,
                Compartment.ocid == current.parent_ocid,
            )
            .first()
        )

    # invertendo para ficar da raiz até o atual
    breadcrumbs.reverse()
    return breadcrumbs


def _get_parent(db: Session, tenancy_id, compartment: Compartment) -> Optional[Compartment]:
    if compartment.parent_ocid is None:
        return None

    return (
        db.query(Compartment)
        .filter(
            Compartment.tenancy_id == tenancy_id,
            Compartment.ocid == compartment.parent_ocid,
        )
        .first()
    )


def _get_children(db: Session, tenancy_id, compartment: Compartment) -> List[Compartment]:
    return (
        db.query(Compartment)
        .filter(
            Compartment.tenancy_id == tenancy_id,
            Compartment.parent_ocid == compartment.ocid,
        )
        .order_by(Compartment.name.asc())
        .all()
    )


def _get_instances_with_config(
    db: Session,
    tenancy_id,
    compartment: Compartment,
) -> List[InstanceWithConfig]:
    """
    Retorna as instâncias do nível atual, incluindo flags de InstanceConfig.
    Caso não exista InstanceConfig, assume managed=False e protection_flag=False.
    """
    # LEFT OUTER JOIN InstanceConfig
    query = (
        db.query(Instance, InstanceConfig)
        .outerjoin(InstanceConfig, InstanceConfig.instance_id == Instance.id)
        .filter(
            Instance.tenancy_id == tenancy_id,
            Instance.compartment_ocid == compartment.ocid,
        )
        .order_by(Instance.display_name.asc())
    )

    results: List[InstanceWithConfig] = []

    for instance, config in query.all():
        results.append(
            InstanceWithConfig(
                id=instance.id,
                ocid=instance.ocid,
                display_name=instance.display_name,
                lifecycle_state=instance.lifecycle_state,
                region=getattr(instance, "region", None),
                availability_domain=getattr(instance, "availability_domain", None),
                managed=bool(getattr(config, "managed", False)) if config else False,
                protection_flag=bool(
                    getattr(config, "protection_flag", False)
                )
                if config
                else False,
            )
        )

    return results


@router.get(
    "/root",
    response_model=CompartmentNavigationResponse,
    summary="Navegação no root compartment da tenancy",
)
def get_root_compartment_navigation(
    tenancy_id: int,  # ou str/UUID
    db: Session = Depends(get_db),
):
    """
    Retorna a navegação hierárquica a partir do root compartment da tenancy.
    """
    tenancy = _get_tenancy_or_404(db, tenancy_id)
    root_compartment = _get_root_compartment(db, tenancy_id)

    breadcrumbs = _build_breadcrumbs(db, tenancy_id, root_compartment)
    parent = _get_parent(db, tenancy_id, root_compartment)
    children = _get_children(db, tenancy_id, root_compartment)
    instances = _get_instances_with_config(db, tenancy_id, root_compartment)

    return CompartmentNavigationResponse(
        tenancy_id=tenancy.id,
        current=CompartmentBase.from_orm(root_compartment),
        breadcrumbs=breadcrumbs,
        parent=CompartmentBase.from_orm(parent) if parent else None,
        children=[CompartmentBase.from_orm(c) for c in children],
        instances=instances,
    )


@router.get(
    "/{compartment_ocid}",
    response_model=CompartmentNavigationResponse,
    summary="Navegação em um compartment específico",
)
def get_compartment_navigation(
    tenancy_id: int,  # ou str/UUID
    compartment_ocid: str,
    db: Session = Depends(get_db),
):
    """
    Retorna a navegação hierárquica para um compartment específico.
    """
    tenancy = _get_tenancy_or_404(db, tenancy_id)
    compartment = _get_compartment_or_404(db, tenancy_id, compartment_ocid)

    breadcrumbs = _build_breadcrumbs(db, tenancy_id, compartment)
    parent = _get_parent(db, tenancy_id, compartment)
    children = _get_children(db, tenancy_id, compartment)
    instances = _get_instances_with_config(db, tenancy_id, compartment)

    return CompartmentNavigationResponse(
        tenancy_id=tenancy.id,
        current=CompartmentBase.from_orm(compartment),
        breadcrumbs=breadcrumbs,
        parent=CompartmentBase.from_orm(parent) if parent else None,
        children=[CompartmentBase.from_orm(c) for c in children],
        instances=instances,
    )
