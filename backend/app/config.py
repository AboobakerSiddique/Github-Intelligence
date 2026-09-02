"""
Application configuration.

Settings are loaded from environment variables (and a local .env file in
development). Nothing here should ever be imported by frontend code, and
secrets are never logged.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App metadata
    app_name: str = "GitHub Intelligence API"
    environment: str = "development"  # development | production
    log_level: str = "INFO"

    # External services (server-side only, never exposed to the frontend)
    github_token: str | None = None
    gemini_api_key: str | None = None

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Caching
    cache_ttl_seconds: int = 300

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor, so .env is only parsed once per process."""
    return Settings()
