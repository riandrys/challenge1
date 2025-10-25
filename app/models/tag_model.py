import uuid
from typing import List

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_model import BaseModel
from app.schemas.tag_schema import TagBase


class PostTagLink(SQLModel, table=True):
    post_id: uuid.UUID = Field(
        foreign_key="post.id", primary_key=True, ondelete="CASCADE"
    )
    tag_id: uuid.UUID = Field(
        foreign_key="tag.id", primary_key=True, ondelete="CASCADE"
    )


class Tag(BaseModel, TagBase, table=True):
    posts: List["Post"] = Relationship(  # type: ignore # noqa: F821
        back_populates="tags",
        link_model=PostTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
