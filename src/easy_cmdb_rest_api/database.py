from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from easy_cmdb_rest_api.config import get_settings


def build_engine(database_url: str, *, echo: bool = False) -> Engine:
    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    return create_engine(database_url, echo=echo, connect_args=connect_args)


_settings = get_settings()
engine = build_engine(_settings.database_url, echo=_settings.echo_sql)


def create_db_and_tables(bind: Engine = engine) -> None:
    SQLModel.metadata.create_all(bind)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
