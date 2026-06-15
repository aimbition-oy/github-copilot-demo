"""Backend service configuration via Pydantic Settings."""

import functools

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    jwt_secret: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./arcade.db"
    cors_origins: str = "http://localhost:5173"
    enable_test_endpoints: bool = False

    model_config = {"env_prefix": "", "case_sensitive": False}


@functools.lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
