from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel
from app.schemas.comment_schema import CommentBase


class Comment(BaseModel, CommentBase, table=True):
    post_id: UUID = Field(foreign_key="post.id", nullable=False, ondelete="CASCADE")
    author_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    post: "Post" = Relationship(  # type: ignore # noqa: F821
        back_populates="comments", sa_relationship_kwargs={"lazy": "selectin"}
    )
    author: "User" = Relationship(  # type: ignore # noqa: F821
        back_populates="comments", sa_relationship_kwargs={"lazy": "selectin"}
    )
