from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or a `.env` file.

    Variables are prefixed with `CMDB_`, e.g. `CMDB_DATABASE_URL`.
    """

    model_config = SettingsConfigDict(
        env_prefix="CMDB_", env_file=".env", extra="ignore"
    )

    app_name: str = "Easy CMDB REST API"
    database_url: str = "sqlite:///./cmdb.db"
    echo_sql: bool = False
    max_body_size: int = 1_048_576  # 1 MiB


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
