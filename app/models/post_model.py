import uuid
from typing import List

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel
from app.models.user_model import User
from app.models.tag_model import Tag, PostTagLink
from app.schemas.post_schema import PostBase


class Post(BaseModel, PostBase, table=True):
    author_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    author: User = Relationship(
        back_populates="posts", sa_relationship_kwargs={"lazy": "selectin"}
    )
    comments: List["Comment"] = Relationship(  # type: ignore # noqa: F821
        back_populates="post", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        back_populates="posts",
        link_model=PostTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
