from datetime import datetime
import uuid

from sqlmodel import SQLModel, Field


class CommentBase(SQLModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    post_id: uuid.UUID
    author_id: uuid.UUID


class CommentUpdate(CommentBase):
    content: str | None = Field(default=None, min_length=1, max_length=1000)  # type: ignore


class CommentPublic(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    is_deleted: bool
