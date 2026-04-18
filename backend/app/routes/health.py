from fastapi import APIRouter

from app.config import get_settings
from app.db import ping_database
from app.models.api import HealthResponse, ServiceStatus
from app.utils.dates import utc_now

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    flags = settings.provider_flags()
    return HealthResponse(
        name=settings.app_name,
        environment=settings.app_env,
        database_connected=await ping_database(),
        demo_mode=settings.demo_mode,
        use_cached_data=settings.use_cached_data,
        services=[
            ServiceStatus(name=name, configured=configured, status="ok" if configured else "missing_config")
            for name, configured in flags.items()
        ],
        server_time=utc_now(),
    )
