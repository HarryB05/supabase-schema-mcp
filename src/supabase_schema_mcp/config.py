"""Configuration from environment (pydantic + python-dotenv)."""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Supabase and database connection settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_project_ref: str = Field(default="", description="Project reference ID")
    supabase_service_role_key: str = Field(default="", description="Service role key")

    supabase_db_host: str = Field(default="", description="Postgres host")
    supabase_db_port: int = Field(default=5432, description="Postgres port")
    supabase_db_name: str = Field(default="postgres", description="Database name")
    supabase_db_user: str = Field(default="", description="Database user")
    supabase_db_password: str = Field(default="", description="Database password")

    db_read_only: bool = Field(
        default=True,
        description="If True, set default_transaction_read_only on connections",
    )

    @property
    def db_connection_configured(self) -> bool:
        """True if enough DB env vars are set to connect."""
        return bool(
            self.supabase_db_host
            and self.supabase_db_name
            and self.supabase_db_user
            and self.supabase_db_password
        )

    @property
    def management_api_configured(self) -> bool:
        """True if Management API credentials are set."""
        return bool(self.supabase_project_ref and self.supabase_service_role_key)


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (loads .env once)."""
    return Settings()


def get_env_warnings() -> list[str]:
    """
    Check for missing .env or missing/empty required env vars.
    Returns a list of warning messages to show at startup.
    """
    warnings: list[str] = []
    env_path = Path.cwd() / ".env"

    if not env_path.exists():
        warnings.append(
            "No .env file found. Copy .env.example to .env and set "
            "SUPABASE_DB_HOST, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD."
        )
        return warnings

    settings = get_settings()

    missing_db: list[str] = []
    if not settings.supabase_db_host:
        missing_db.append("SUPABASE_DB_HOST")
    if not settings.supabase_db_user:
        missing_db.append("SUPABASE_DB_USER")
    if not settings.supabase_db_password:
        missing_db.append("SUPABASE_DB_PASSWORD")
    if not settings.supabase_db_name:
        missing_db.append("SUPABASE_DB_NAME")

    if missing_db:
        warnings.append(
            ".env exists but required database variables are missing or empty: "
            + ", ".join(missing_db)
            + ". Schema tools will fail until these are set."
        )

    return warnings
