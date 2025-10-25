import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str = Field(min_length=3, max_length=255, index=True)
    content: str = Field(min_length=10)


class PostCreate(SQLModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10)
    tag_ids: list[int] = Field(default_factory=list)


class PostUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=10)
    tag_ids: list[uuid.UUID] = []


class PostPublic(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    is_deleted: bool


# Schema for reading a post with author info
class PostReadWithAuthor(PostPublic):
    author: "UserPublic"  # type: ignore # noqa: F821


# Schema for reading a post with all relationships
class PostReadWithRelations(PostReadWithAuthor):
    tags: list["TagRead"] = []  # type: ignore # noqa: F821
    comments: list["CommentRead"] = []  # type: ignore # noqa: F821
