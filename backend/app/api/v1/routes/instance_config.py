# app/api/v1/instance_config.py

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.instance import Instance
from app.models.instance_config import InstanceConfig
from app.schemas.instance_config import (
    InstanceConfigResponse,
    InstanceConfigUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()

DbSessionDep = Annotated[Session, Depends(get_db)]


def _get_instance_or_404(db: Session, instance_id: UUID) -> Instance:
    instance = (
        db.query(Instance)
        .filter(Instance.id == instance_id)
        .first()
    )
    if not instance:
        logger.info("Instância não encontrada ao acessar config: %s", instance_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found",
        )
    return instance


@router.get(
    "/instances/{instance_id}/config",
    response_model=InstanceConfigResponse,
)
def get_instance_config(
    instance_id: UUID,
    db: DbSessionDep,
) -> InstanceConfigResponse:
    """
    Retorna a configuração da instância.

    - Se a instância não existir → 404.
    - Se não existir config em InstanceConfig → objeto default
      (managed=False, protection_flag=False, timezone='UTC', configurado=False).
    """
    instance = _get_instance_or_404(db, instance_id)

    cfg: InstanceConfig | None = (
        db.query(InstanceConfig)
        .filter(InstanceConfig.instance_id == instance.id)
        .first()
    )

    if cfg is None:
        # Retorna objeto default, sem registro persistido
        logger.debug(
            "Nenhuma configuração encontrada para a instância %s, retornando default",
            instance.id,
        )
        return InstanceConfigResponse(
            instance_id=instance.id,
            # demais campos usam os defaults do schema
            configurado=False,
        )

    # Usa from_attributes=True para preencher todos os campos que batem com o modelo
    response = InstanceConfigResponse.model_validate(cfg)
    # Marca como configurado
    return response.model_copy(update={"configurado": True})


@router.put(
    "/instances/{instance_id}/config",
    response_model=InstanceConfigResponse,
)
def upsert_instance_config(
    instance_id: UUID,
    payload: InstanceConfigUpdate,
    db: DbSessionDep,
) -> InstanceConfigResponse:
    """
    Cria ou atualiza a configuração da instância (upsert).

    - 404 se a instância não existir.
    - Se não houver config, cria.
    - Se já houver config, atualiza campos a partir do payload.
    """
    instance = _get_instance_or_404(db, instance_id)

    cfg: InstanceConfig | None = (
        db.query(InstanceConfig)
        .filter(InstanceConfig.instance_id == instance.id)
        .first()
    )

    if cfg is None:
        logger.info(
            "Criando nova configuração para a instância %s", instance.id
        )
        cfg = InstanceConfig(instance_id=instance.id)
        db.add(cfg)

    # Aplica os campos do payload no modelo (update parcial)
    update_data = payload.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        # Garante que só aplica atributos que existem no modelo InstanceConfig
        if hasattr(cfg, field_name):
            setattr(cfg, field_name, value)
        else:
            logger.debug(
                "Campo %s não existe no modelo InstanceConfig, ignorando",
                field_name,
            )

    db.commit()
    db.refresh(cfg)

    response = InstanceConfigResponse.model_validate(cfg)
    return response.model_copy(update={"configurado": True})


@router.delete(
    "/instances/{instance_id}/config",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_instance_config(
    instance_id: UUID,
    db: DbSessionDep,
) -> None:
    """
    Remove a configuração de uma instância (reset).

    - 404 se a instância não existir.
    - Se não houver config, operação é idempotente (retorna 204 mesmo assim).
    """
    instance = _get_instance_or_404(db, instance_id)

    cfg: InstanceConfig | None = (
        db.query(InstanceConfig)
        .filter(InstanceConfig.instance_id == instance.id)
        .first()
    )

    if cfg is None:
        logger.debug(
            "Nenhuma configuração para deletar na instância %s, "
            "tratando como idempotente",
            instance.id,
        )
        return

    logger.info(
        "Removendo configuração da instância %s (InstanceConfig.id=%s)",
        instance.id,
        getattr(cfg, "id", None),
    )

    db.delete(cfg)
    db.commit()
    # 204 No Content
    return
