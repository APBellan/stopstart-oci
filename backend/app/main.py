# backend/app/main.py

import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import get_settings
from app.api.v1.routes import health as health_routes
from app.api.v1.routes import compartments as compartments_routes  # 👈 novo import
from app.api.v1.routes import instance_config as instance_config_routes
from app.db.session import SessionLocal
from app.models.base import Base  # garante que Base está disponível

logger = logging.getLogger(__name__)
settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
    )

    api_v1_prefix = "/api/v1"

    # Health check
    app.include_router(
        health_routes.router,
        prefix=api_v1_prefix,
        tags=["health"],
    )
    
    # Rotas de configuração de instância
    app.include_router(
        instance_config_routes.router,
        prefix=api_v1_prefix,
        tags=["instance-config"],
    )

    # Navegação hierárquica de compartments
    app.include_router(
        compartments_routes.router,
        prefix=api_v1_prefix,
        tags=["compartments"],
    )

    @app.on_event("startup")
    def startup_db_check() -> None:
        """
        Na subida da API, testa a conexão com o banco.
        Se der erro aqui, fica explícito no log.
        """
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            logger.info("✅ Conexão com o banco estabelecida com sucesso")
        except Exception as exc:
            logger.exception("❌ Erro ao conectar no banco de dados")
            # Relevante em ambiente de container: deixar falhar rápido
            raise exc
        finally:
            db.close()

    return app


app = create_app()
