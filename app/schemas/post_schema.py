from uuid import UUID
from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel, Field

from app.schemas.comment_schema import CommentPublic
from app.schemas.tag_schema import TagPublic
from app.schemas.user_schema import UserPublic


class PostBase(SQLModel):
    title: str = Field(min_length=3, max_length=255, index=True)
    content: str = Field(min_length=10)


class PostCreate(SQLModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10)
    tag_ids: list[UUID] = Field(default_factory=list)


class PostUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=10)
    tag_ids: list[UUID] = Field(default_factory=list)


class PostPublic(PostBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    is_deleted: bool


class PostReadWithAuthor(PostPublic):
    author: UserPublic


class PostPublicWithRelations(PostReadWithAuthor):
    tags: list[TagPublic] = []
    comments: list[CommentPublic] = []

    @field_validator("comments", mode="before")
    @classmethod
    def filter_deleted_comments(cls, v):
        return [comment for comment in v if not comment.is_deleted]
