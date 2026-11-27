from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class CIType(StrEnum):
    SERVER = "server"
    VIRTUAL_MACHINE = "virtual_machine"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    SERVICE = "service"
    OTHER = "other"


class CIStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class ConfigurationItemBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    ci_type: CIType = Field(index=True)
    status: CIStatus = Field(default=CIStatus.PLANNED, index=True)
    description: str | None = Field(default=None, max_length=2000)
    owner: str | None = Field(default=None, max_length=255)


class ConfigurationItem(ConfigurationItemBase, table=True):
    __tablename__ = "configuration_item"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ConfigurationItemCreate(ConfigurationItemBase):
    pass


class ConfigurationItemUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    ci_type: CIType | None = None
    status: CIStatus | None = None
    description: str | None = Field(default=None, max_length=2000)
    owner: str | None = Field(default=None, max_length=255)


class ConfigurationItemPublic(ConfigurationItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
