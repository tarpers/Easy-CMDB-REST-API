from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from easy_cmdb_rest_api.database import SessionDep

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]


@router.get("")
def health_check(session: SessionDep) -> HealthStatus:
    session.exec(select(1)).one()
    return HealthStatus(status="ok", database="ok")
