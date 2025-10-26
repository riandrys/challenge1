from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel, Field


class TagBase(SQLModel):
    name: str = Field(min_length=1, max_length=50, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255)


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: str | None = Field(default=None, min_length=1, max_length=50)  # type: ignore
    description: str | None = Field(default=None, max_length=255)


class TagPublic(TagBase):
    id: UUID
    created_at: datetime
    is_deleted: bool
