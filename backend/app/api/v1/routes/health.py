from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Healthcheck da API")
async def healthcheck():
    return {"status": "ok"}
