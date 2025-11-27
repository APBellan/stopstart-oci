from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import health as health_routes

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
    )

    # Versão v1 da API
    api_v1_prefix = "/api/v1"
    app.include_router(
        health_routes.router,
        prefix=api_v1_prefix,
        tags=["health"],
    )

    return app


app = create_app()
