from fastapi import APIRouter

from app.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])

API_VERSION = "0.1.0"


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns basic service status. Used by uptime monitors and local development.",
)
async def get_health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version=API_VERSION,
    )
