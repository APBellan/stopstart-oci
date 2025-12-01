# backend/app/cli.py
from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Mapping

import oci
from sqlalchemy.orm import Session

from .db.session import SessionLocal  # ajuste se o nome for diferente
from .services.oci_inventory_sync import sync_inventory

logger = logging.getLogger(__name__)


def _load_oci_config(profile: str | None = None, config_file: str | None = None) -> Mapping[str, Any]:
    """
    Carrega o arquivo de configuração OCI (por padrão ~/.oci/config).

    :param profile: nome do profile no arquivo (ex: "DEFAULT", "prod", etc.)
    :param config_file: caminho customizado para o arquivo de config
    """
    kwargs: dict[str, Any] = {}
    if config_file:
        kwargs["file_location"] = config_file
    if profile:
        kwargs["profile_name"] = profile

    return oci.config.from_file(**kwargs)


def cmd_sync_oci_inventory(profile: str | None, config_file: str | None) -> None:
    """
    Executa o serviço de sincronização de inventário OCI (compartments + instances).
    """
    logger.info("Carregando configuração OCI (profile=%r, config_file=%r)", profile, config_file)
    oci_config = _load_oci_config(profile=profile, config_file=config_file)

    db: Session = SessionLocal()
    try:
        logger.info("Iniciando sincronização de inventário OCI...")
        sync_inventory(db, oci_config)
        db.commit()
        logger.info("Sincronização de inventário OCI concluída com sucesso.")
    except Exception:
        logger.exception("Erro ao executar sincronização de inventário OCI. Fazendo rollback.")
        db.rollback()
        raise
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.cli",
        description="Ferramentas de linha de comando da aplicação Stop/Start OCI",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nível de log (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------
    # sync-oci-inventory
    # ------------------------------------------------------------------
    sync_parser = subparsers.add_parser(
        "sync-oci-inventory",
        help="Sincroniza a árvore de compartments e instâncias de compute a partir do OCI.",
    )
    sync_parser.add_argument(
        "--profile",
        dest="profile",
        default=None,
        help="Profile do arquivo ~/.oci/config (default: profile padrão).",
    )
    sync_parser.add_argument(
        "--config-file",
        dest="config_file",
        default=None,
        help="Caminho para o arquivo de configuração OCI (default: ~/.oci/config).",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    # Configura logging básico
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    if args.command == "sync-oci-inventory":
        cmd_sync_oci_inventory(profile=args.profile, config_file=args.config_file)
    else:
        parser.error(f"Comando desconhecido: {args.command!r}")


if __name__ == "__main__":
    main()
