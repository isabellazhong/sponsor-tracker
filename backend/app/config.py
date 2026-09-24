"""Application settings, loaded from the environment (and an optional .env file)."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sponsorship Tracker API"
    environment: str = "development"
    debug: bool = False

    # postgresql+asyncpg://user:password@host:port/database
    database_url: str = "postgresql+asyncpg://sponsor:sponsor@localhost:5432/sponsor_tracker"
    test_database_url: str | None = None
    db_echo: bool = False

    session_secret: str = "dev-only-insecure-change-me"

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Accept a comma-separated string as well as pydantic's JSON list form."""
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def effective_test_database_url(self) -> str:
        """The test database URL, defaulting to the main database with a _test suffix."""
        if self.test_database_url:
            return self.test_database_url
        base, _, name = self.database_url.rpartition("/")
        return f"{base}/{name}_test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
