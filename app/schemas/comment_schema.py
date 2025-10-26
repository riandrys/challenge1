from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel, Field


class CommentBase(SQLModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    post_id: UUID
    author_id: UUID


class CommentUpdate(CommentBase):
    content: str | None = Field(default=None, min_length=1, max_length=1000)  # type: ignore


class CommentPublic(CommentBase):
    id: UUID
    post_id: UUID
    author_id: UUID
    created_at: datetime
    is_deleted: bool
