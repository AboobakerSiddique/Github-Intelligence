"""
GitHub Intelligence API — application entrypoint.

Responsibilities of this module are intentionally limited to:
  - constructing the FastAPI app
  - wiring middleware (CORS)
  - registering routers

Business logic lives in `services/`, GitHub access lives in `clients/`.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.analytics import router as analytics_router
from app.api.compare import router as compare_router
from app.api.export import router as export_router
from app.api.health import router as health_router
from app.api.repositories import router as repositories_router
from app.clients.gemini_client import GeminiClient
from app.clients.github_client import GitHubClient
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s | environment=%s",
        settings.app_name,
        settings.environment,
    )
    app.state.github_client = GitHubClient()
    app.state.gemini_client = GeminiClient()
    yield
    await app.state.github_client.aclose()
    await app.state.gemini_client.aclose()
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for GitHub Intelligence — analyzes public GitHub "
        "repositories and produces engineering insights."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    # Browser extension content scripts run from a chrome-extension:// origin.
    # These endpoints only ever return public, read-only repository data, so
    # opening CORS to any extension origin carries no meaningful risk.
    allow_origin_regex=r"^chrome-extension://.*$",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(repositories_router)
app.include_router(analytics_router)
app.include_router(ai_router)
app.include_router(compare_router)
app.include_router(export_router)
