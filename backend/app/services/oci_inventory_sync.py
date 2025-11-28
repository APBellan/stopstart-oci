from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

import oci
from oci.pagination import list_call_get_all_results
from sqlalchemy.orm import Session

from ..models.compartment import Compartment
from ..models.instance import Instance

logger = logging.getLogger(__name__)


@dataclass
class OCIClients:
    """Container simples para agrupar os clients OCI usados no sync."""
    identity: oci.identity.IdentityClient
    compute: oci.core.ComputeClient
    tenancy_ocid: str
    region: str


# ============================================================
# Funções públicas (API do serviço)
# ============================================================

def sync_inventory(db: Session, oci_config: Mapping[str, Any]) -> None:
    """
    Sincroniza completamente o inventário:
    - Árvore de compartments da tenancy
    - Instâncias de compute por compartment

    Não faz commit. O commit/rollback é responsabilidade de quem chamou.

    :param db: sessão SQLAlchemy já aberta
    :param oci_config: dict de configuração OCI (ex: oci.config.from_file())
    """
    clients = _build_oci_clients(oci_config)
    logger.info("Iniciando sync completo de inventário OCI para tenancy %s", clients.tenancy_ocid)

    sync_compartments(db, clients)
    sync_instances(db, clients)

    logger.info("Sync completo de inventário OCI finalizado para tenancy %s", clients.tenancy_ocid)


def sync_compartments(db: Session, clients: OCIClients) -> List[Compartment]:
    """
    Sincroniza a tabela compartments com a árvore de compartments da tenancy.

    - Insere/atualiza compartments existentes no OCI.
    - Marca como inativos (is_active = False) os que não existirem mais no OCI.

    :param db: sessão SQLAlchemy
    :param clients: objeto com IdentityClient, ComputeClient, tenancy_ocid, region
    :return: lista de compartments sincronizados (ativos após o sync)
    """
    tenancy_ocid = clients.tenancy_ocid
    identity = clients.identity

    logger.info("Buscando árvore de compartments no OCI para tenancy %s", tenancy_ocid)

    tenancy = identity.get_tenancy(tenancy_ocid).data
    tenancy_name = tenancy.name

    remote_nodes = _fetch_compartment_tree(identity, tenancy_ocid, tenancy_name)
    logger.info("Foram retornados %d nós de árvore (incluindo raiz tenancy).", len(remote_nodes))

    # Busca tudo que já temos dessa tenancy no banco
    existing: Dict[str, Compartment] = {
        c.compartment_ocid: c
        for c in db.query(Compartment).filter(Compartment.tenancy_ocid == tenancy_ocid)
    }

    updated_or_created: List[Compartment] = []
    remote_ocids: Set[str] = set()

    for node in remote_nodes:
        ocid = node["compartment_ocid"]
        remote_ocids.add(ocid)

        comp = existing.get(ocid)
        if comp is None:
            comp = Compartment(
                tenancy_ocid=tenancy_ocid,
                compartment_ocid=ocid,
                name=node["name"],
                description=node.get("description"),
                parent_ocid=node.get("parent_ocid"),
                path=node["path"],
                is_tenancy_root=node["is_tenancy_root"],
            )
            # Marca ativo, se o modelo tiver esse campo
            if hasattr(comp, "is_active"):
                setattr(comp, "is_active", True)
            db.add(comp)
            existing[ocid] = comp
        else:
            comp.name = node["name"]
            comp.description = node.get("description")
            comp.parent_ocid = node.get("parent_ocid")
            comp.path = node["path"]
            comp.is_tenancy_root = node["is_tenancy_root"]
            if hasattr(comp, "is_active"):
                setattr(comp, "is_active", True)

        updated_or_created.append(comp)

    # Flush para garantir IDs (UUID) gerados antes de ajustarmos parent_id
    db.flush()

    # Atualiza parent_id (FK) com base no parent_ocid usamos acima
    ocid_to_model: Dict[str, Compartment] = {
        c.compartment_ocid: c for c in existing.values()
    }

    for comp in existing.values():
        if comp.parent_ocid:
            parent = ocid_to_model.get(comp.parent_ocid)
            if parent is not None:
                comp.parent_id = parent.id  # type: ignore[attr-defined]
        else:
            comp.parent_id = None  # type: ignore[attr-defined]

    # Marca como inativos os compartments que sumiram do OCI
    missing = [c for ocid, c in existing.items() if ocid not in remote_ocids]
    for comp in missing:
        if hasattr(comp, "is_active"):
            setattr(comp, "is_active", False)

    logger.info(
        "Sync de compartments concluído. Ativos/atualizados: %d, marcados inativos: %d",
        len(updated_or_created),
        len(missing),
    )

    db.flush()
    return updated_or_created


def sync_instances(db: Session, clients: OCIClients) -> List[Instance]:
    """
    Sincroniza a tabela instances com as instâncias de compute da tenancy (na região do config).

    - Lista instâncias por compartment ativo.
    - Insere/atualiza instâncias encontradas.
    - Marca como inativas (is_active = False) as instâncias que não aparecerem mais no OCI.

    :param db: sessão SQLAlchemy
    :param clients: objeto com IdentityClient, ComputeClient, tenancy_ocid, region
    :return: lista de instâncias sincronizadas (ativas após o sync)
    """
    tenancy_ocid = clients.tenancy_ocid
    region = clients.region
    compute = clients.compute

    logger.info(
        "Iniciando sync de instâncias para tenancy %s na região %s",
        tenancy_ocid,
        region,
    )

    # Busca compartments ativos dessa tenancy
    compartments_q = db.query(Compartment).filter(
        Compartment.tenancy_ocid == tenancy_ocid
    )
    if hasattr(Compartment, "is_active"):
        compartments_q = compartments_q.filter(getattr(Compartment, "is_active") == True)  # noqa: E712

    compartments: List[Compartment] = list(compartments_q)
    compartment_by_ocid: Dict[str, Compartment] = {
        c.compartment_ocid: c for c in compartments
    }

    # Todas as instâncias já cadastradas para essa região
    existing_instances: Dict[str, Instance] = {
        inst.instance_ocid: inst
        for inst in db.query(Instance).filter(Instance.region == region)
    }

    remote_instance_ocids: Set[str] = set()
    updated_or_created: List[Instance] = []

    active_states = {
        "PROVISIONING",
        "RUNNING",
        "STOPPED",
        "STOPPING",
        "STARTING",
    }

    for comp in compartments:
        comp_ocid = comp.compartment_ocid
        logger.debug(
            "Listando instâncias em compartment %s (%s)",
            comp.name,
            comp_ocid,
        )

        # Pega todas as instâncias do compartment (paginação automática)
        response = list_call_get_all_results(
            compute.list_instances,
            compartment_id=comp_ocid,
        )

        for inst in response.data:
            # Ignora instâncias terminadas (não retornam normalmente, mas por segurança)
            if inst.lifecycle_state not in active_states:
                continue

            inst_ocid = inst.id
            remote_instance_ocids.add(inst_ocid)

            db_instance = existing_instances.get(inst_ocid)
            if db_instance is None:
                db_instance = Instance(
                    instance_ocid=inst_ocid,
                    compartment_ocid=inst.compartment_id,
                    compartment_id=comp.id,
                    display_name=inst.display_name,
                    region=region,
                    availability_domain=inst.availability_domain,
                    lifecycle_state=inst.lifecycle_state,
                    shape=inst.shape,
                    hostname=getattr(inst, "hostname_label", None),
                    image_ocid=getattr(inst, "image_id", None),
                    # tags
                    freeform_tags=getattr(inst, "freeform_tags", None),
                    defined_tags=getattr(inst, "defined_tags", None),
                    # cache de path do compartment para facilitar filtros
                    compartment_path_cache=comp.path,
                )
                if hasattr(db_instance, "is_active"):
                    setattr(db_instance, "is_active", True)

                db.add(db_instance)
                existing_instances[inst_ocid] = db_instance
            else:
                # Atualiza campos principais
                db_instance.compartment_ocid = inst.compartment_id
                db_instance.compartment_id = comp.id
                db_instance.display_name = inst.display_name
                db_instance.region = region
                db_instance.availability_domain = inst.availability_domain
                db_instance.lifecycle_state = inst.lifecycle_state
                db_instance.shape = inst.shape
                db_instance.hostname = getattr(inst, "hostname_label", None)
                db_instance.image_ocid = getattr(inst, "image_id", None)
                db_instance.freeform_tags = getattr(inst, "freeform_tags", None)
                db_instance.defined_tags = getattr(inst, "defined_tags", None)
                db_instance.compartment_path_cache = comp.path
                if hasattr(db_instance, "is_active"):
                    setattr(db_instance, "is_active", True)

            updated_or_created.append(db_instance)

    # Instâncias que existiam no banco, mas não apareceram mais no OCI
    missing_instances = [
        inst for ocid, inst in existing_instances.items()
        if ocid not in remote_instance_ocids
    ]
    for inst in missing_instances:
        if hasattr(inst, "is_active"):
            setattr(inst, "is_active", False)

    logger.info(
        "Sync de instâncias concluído. Ativas/atualizadas: %d, marcadas inativas: %d",
        len(updated_or_created),
        len(missing_instances),
    )

    db.flush()
    return updated_or_created


# ============================================================
# Helpers internos
# ============================================================

def _build_oci_clients(oci_config: Mapping[str, Any]) -> OCIClients:
    """
    Constrói os clients OCI usados no sync a partir do dict de configuração.

    :param oci_config: dict de configuração (ex: oci.config.from_file())
    """
    config_dict = dict(oci_config)
    tenancy_ocid = config_dict["tenancy"]
    region = config_dict["region"]

    identity_client = oci.identity.IdentityClient(config_dict)
    compute_client = oci.core.ComputeClient(config_dict)

    return OCIClients(
        identity=identity_client,
        compute=compute_client,
        tenancy_ocid=tenancy_ocid,
        region=region,
    )


def _fetch_compartment_tree(
    identity_client: oci.identity.IdentityClient,
    tenancy_ocid: str,
    tenancy_name: str,
) -> List[Dict[str, Any]]:
    """
    Retorna a árvore de compartments a partir do OCI em formato simplificado.

    Inclui um nó artificial para a raiz da tenancy (is_tenancy_root=True).

    Estrutura de cada dict retornado:
    {
        "compartment_ocid": str,
        "name": str,
        "description": Optional[str],
        "parent_ocid": Optional[str],
        "is_tenancy_root": bool,
        "path": str,
    }
    """
    # Lista todos os compartments (subárvore completa)
    list_result = list_call_get_all_results(
        identity_client.list_compartments,
        compartment_id=tenancy_ocid,
        compartment_id_in_subtree=True,
        access_level="ANY",
    )

    raw_compartments = list_result.data

    # Filtra apenas ativos
    active_compartments = [
        c for c in raw_compartments
        if getattr(c, "lifecycle_state", None) == "ACTIVE"
    ]

    # Monta mapa simples de ocid -> dados
    nodes: Dict[str, Dict[str, Any]] = {}

    # Nó raiz (tenancy)
    nodes[tenancy_ocid] = {
        "compartment_ocid": tenancy_ocid,
        "name": tenancy_name,
        "description": None,
        "parent_ocid": None,
        "is_tenancy_root": True,
    }

    # Demais compartments
    for c in active_compartments:
        comp_ocid = c.id
        parent_ocid = c.compartment_id or tenancy_ocid

        nodes[comp_ocid] = {
            "compartment_ocid": comp_ocid,
            "name": c.name,
            "description": getattr(c, "description", None),
            "parent_ocid": parent_ocid,
            "is_tenancy_root": False,
        }

    # Calcula path de cada nó (ex: /tenancy/parent/child)
    path_cache: Dict[str, str] = {}

    def build_path(ocid: str) -> str:
        if ocid in path_cache:
            return path_cache[ocid]

        node = nodes[ocid]
        parent_ocid = node.get("parent_ocid")

        if node["is_tenancy_root"] or not parent_ocid:
            path = f"/{node['name']}"
        else:
            parent_path = build_path(parent_ocid)
            path = f"{parent_path}/{node['name']}"

        path_cache[ocid] = path
        return path

    for ocid in nodes.keys():
        build_path(ocid)

    # Copia paths para os dicts
    result: List[Dict[str, Any]] = []
    for ocid, node in nodes.items():
        node_copy = dict(node)
        node_copy["path"] = path_cache[ocid]
        result.append(node_copy)

    return result
