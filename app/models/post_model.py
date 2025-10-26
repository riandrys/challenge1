from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel
from app.models.tag_model import PostTagLink
from app.schemas.post_schema import PostBase


class Post(BaseModel, PostBase, table=True):
    author_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    author: "User" = Relationship(  # type: ignore # noqa: F821
        back_populates="posts", sa_relationship_kwargs={"lazy": "selectin"}
    )
    comments: list["Comment"] = Relationship(  # type: ignore # noqa: F821
        back_populates="post", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: list["Tag"] = Relationship(  # type: ignore # noqa: F821
        back_populates="posts",
        link_model=PostTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
