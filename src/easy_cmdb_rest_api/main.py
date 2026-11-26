from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from easy_cmdb_rest_api.config import get_settings
from easy_cmdb_rest_api.database import create_db_and_tables
from easy_cmdb_rest_api.routers import configuration_items, health


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        max_body_size=settings.max_body_size,
    )
    app.include_router(health.router)
    app.include_router(configuration_items.router)
    return app


app = create_app()
