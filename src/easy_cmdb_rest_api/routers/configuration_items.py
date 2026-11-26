from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlmodel import col, select

from easy_cmdb_rest_api.database import SessionDep
from easy_cmdb_rest_api.models import (
    CIStatus,
    CIType,
    ConfigurationItem,
    ConfigurationItemCreate,
    ConfigurationItemPublic,
    ConfigurationItemUpdate,
    utcnow,
)

router = APIRouter(prefix="/configuration-items", tags=["configuration-items"])

CIIdPath = Annotated[int, Path(ge=1, description="The configuration item ID")]


def get_ci_or_404(session: SessionDep, ci_id: int) -> ConfigurationItem:
    ci = session.get(ConfigurationItem, ci_id)
    if ci is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration item not found",
        )
    return ci


@router.get("/")
def list_configuration_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ci_type: CIType | None = None,
    ci_status: Annotated[CIStatus | None, Query(alias="status")] = None,
) -> list[ConfigurationItemPublic]:
    statement = select(ConfigurationItem)
    if ci_type is not None:
        statement = statement.where(ConfigurationItem.ci_type == ci_type)
    if ci_status is not None:
        statement = statement.where(ConfigurationItem.status == ci_status)
    statement = (
        statement.order_by(col(ConfigurationItem.id)).offset(offset).limit(limit)
    )
    items = session.exec(statement).all()
    return [ConfigurationItemPublic.model_validate(ci) for ci in items]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_configuration_item(
    session: SessionDep, ci_in: ConfigurationItemCreate
) -> ConfigurationItemPublic:
    ci = ConfigurationItem.model_validate(ci_in)
    session.add(ci)
    session.commit()
    session.refresh(ci)
    return ConfigurationItemPublic.model_validate(ci)


@router.get("/{ci_id}")
def read_configuration_item(
    session: SessionDep, ci_id: CIIdPath
) -> ConfigurationItemPublic:
    return ConfigurationItemPublic.model_validate(get_ci_or_404(session, ci_id))


@router.patch("/{ci_id}")
def update_configuration_item(
    session: SessionDep, ci_id: CIIdPath, ci_in: ConfigurationItemUpdate
) -> ConfigurationItemPublic:
    ci = get_ci_or_404(session, ci_id)
    ci.sqlmodel_update(ci_in.model_dump(exclude_unset=True))
    ci.updated_at = utcnow()
    session.add(ci)
    session.commit()
    session.refresh(ci)
    return ConfigurationItemPublic.model_validate(ci)


@router.delete("/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_configuration_item(session: SessionDep, ci_id: CIIdPath) -> None:
    ci = get_ci_or_404(session, ci_id)
    session.delete(ci)
    session.commit()
