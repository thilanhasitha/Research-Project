from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "valuation-engine"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    api_prefix: str = "/api"
    api_version: str = "v1"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "valuation_engine"

    cse_base_url: str = "https://www.cse.lk"
    cse_api_key: str | None = None
    http_timeout_seconds: int = 15

    # Gemini API settings
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-pro"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VE_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
